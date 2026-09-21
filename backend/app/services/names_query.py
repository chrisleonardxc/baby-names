"""Filtered/sorted/paginated name search, done entirely in SQL.

Everything that decides *which* names match and in what order runs as one SQLite
query that returns only the requested page. Per-country stats, trends, and
reactions are then fetched for just those (at most page_size) names.

List-valued parameters (countries, sexes, name ids, favorited pairs) are passed as
a single JSON bind parameter and expanded with json_each(), so no query ever
builds an `IN (?, ?, ...)` list whose size depends on the data -- those used to
hit SQLite's "too many SQL variables" limit on broad filters.
"""

import json
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session

from shared.config import settings
from shared.models import DimName, NameReaction, Person


@dataclass
class NameFilters:
    sex: str = "ALL"  # M | F | ALL
    unisex_only: bool = False
    countries: list[str] | None = None
    match_mode: str = "any"  # any | all
    search: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    rank_max: int | None = None
    starting_letter: str | None = None
    length_min: int | None = None
    length_max: int | None = None
    syllables_min: int | None = None
    syllables_max: int | None = None
    trend: str = "any"  # rising | falling | stable | any
    viewer: str | None = None
    exclude_vetoed: bool = False
    sort_by: str = "popularity"  # popularity | alpha | length
    sort_dir: str = "asc"
    page: int = 1
    page_size: int = 50
    restrict_name_sex: set[tuple[int, str]] | None = None


# Sorts unranked names after every ranked one (ascending), like float("inf") did.
_UNRANKED = 1 << 62


def _all_person_keys() -> list[str]:
    return [settings.person_a_key, settings.person_b_key]


def _json_in(column: str, param: str) -> str:
    return f"{column} IN (SELECT value FROM json_each(:{param}))"


def _literal_in(column: str, prefix: str, values: list[str], params: dict) -> str:
    """For short, bounded lists (sexes, countries). Unlike json_each, these let the
    planner see the list and use the (country_code, sex, year) index."""
    names = []
    for i, value in enumerate(values):
        params[f"{prefix}_{i}"] = value
        names.append(f":{prefix}_{i}")
    return f"{column} IN ({', '.join(names)})"


def _dim_name_conditions(f: NameFilters, params: dict) -> list[str]:
    conds = []
    search_term = f.search.strip().lower() if f.search else None
    if search_term:
        conds.append("instr(name_lower, :search) > 0")
        params["search"] = search_term
    if f.starting_letter:
        conds.append("upper(starting_letter) = :starting_letter")
        params["starting_letter"] = f.starting_letter.upper()
    if f.length_min is not None:
        conds.append("length >= :length_min")
        params["length_min"] = f.length_min
    if f.length_max is not None:
        conds.append("length <= :length_max")
        params["length_max"] = f.length_max
    if f.syllables_min is not None:
        conds.append("coalesce(syllable_count, 0) >= :syllables_min")
        params["syllables_min"] = f.syllables_min
    if f.syllables_max is not None:
        conds.append("coalesce(syllable_count, 0) <= :syllables_max")
        params["syllables_max"] = f.syllables_max
    return conds


def _stats_ctes(
    f: NameFilters,
    sexes: list[str],
    countries: list[str] | None,
    params: dict,
    *,
    with_trend: bool,
    page_name_ids: list[int] | None = None,
) -> str:
    """CTEs ending in `stats(name_id, country_code, sex, best_rank, total_count,
    first_year, last_year, trend)` -- one row per (name, country, sex) that passes
    the sex/country/rank/year filters. Filters that are per-name or per-(name, sex)
    are pushed down here too, so the year-range aggregation only touches rows that
    can possibly match."""
    base = [_literal_in("sex", "sex", sexes, params)]
    if countries:
        base.append(_literal_in("country_code", "country", countries, params))
    if page_name_ids is not None:
        params["page_name_ids"] = json.dumps(page_name_ids)
        base.append(_json_in("name_id", "page_name_ids"))
    if f.restrict_name_sex is not None:
        params["restrict"] = json.dumps(sorted(f.restrict_name_sex))
        base.append(
            "(name_id, sex) IN (SELECT json_extract(value, '$[0]'), json_extract(value, '$[1]')"
            " FROM json_each(:restrict))"
        )
    dim_conds = _dim_name_conditions(f, params)
    if dim_conds:
        # The unary + stops SQLite from driving the query off this list (one index
        # probe per matching name -- tens of thousands for a length or letter
        # filter); it's applied as a cheap set lookup on rows found via the
        # country/sex/year/rank indexes instead.
        base.append(f"+name_id IN (SELECT id FROM dim_name WHERE {' AND '.join(dim_conds)})")
    if f.rank_max is not None:
        params["rank_max"] = f.rank_max

    if f.year_min is None and f.year_max is None:
        # Fast path: whole-history stats (and trend) precomputed at ingestion time.
        if f.rank_max is not None:
            base.append("best_rank IS NOT NULL AND best_rank <= :rank_max")
        return f"""
        stats AS (
            SELECT name_id, country_code, sex, best_rank, total_count, first_year, last_year,
                   {"trend" if with_trend else "NULL"} AS trend
            FROM fact_name_country_sex_agg
            WHERE {" AND ".join(base)}
        )"""

    # A year range is selected: aggregate the yearly facts inside that range.
    if f.year_min is not None:
        base.append("year >= :year_min")
        params["year_min"] = f.year_min
    if f.year_max is not None:
        base.append("year <= :year_max")
        params["year_max"] = f.year_max

    where = " AND ".join(base)
    ctes = ""
    if f.rank_max is not None:
        # Find the (name, country, sex) groups that reached the rank cap in range
        # first -- a small set -- and only aggregate (and trend) those groups'
        # years, rather than grouping every row in the range and filtering after.
        ctes = f"""
        candidates AS MATERIALIZED (
            SELECT DISTINCT name_id, country_code, sex
            FROM fact_name_year
            WHERE {where} AND rank <= :rank_max
        ),"""
        where += " AND (name_id, country_code, sex) IN (SELECT * FROM candidates)"
    # With a trend, yr is read twice (stats + trend), so compute it once; without
    # one, copying it into a temp table is pure overhead.
    ctes += f"""
        yr AS {"MATERIALIZED" if with_trend else "NOT MATERIALIZED"} (
            SELECT name_id, country_code, sex, year, rank, count
            FROM fact_name_year
            WHERE {where}
        ),
        yr_agg AS (
            SELECT name_id, country_code, sex,
                   MIN(rank) AS best_rank, coalesce(SUM(count), 0) AS total_count,
                   MIN(year) AS first_year, MAX(year) AS last_year
            FROM yr
            GROUP BY name_id, country_code, sex
        )"""
    if not with_trend:
        return ctes + """,
        stats AS (SELECT *, NULL AS trend FROM yr_agg)"""

    # Same rule as shared.trend.compute_trend, over just the ranked years in range:
    # compare the average rank of the earliest third of years with the latest third.
    return ctes + """,
        ranked AS (
            SELECT name_id, country_code, sex, rank,
                   ROW_NUMBER() OVER w AS rn,
                   COUNT(*) OVER (PARTITION BY name_id, country_code, sex) AS n
            FROM yr
            WHERE rank IS NOT NULL
            WINDOW w AS (PARTITION BY name_id, country_code, sex ORDER BY year, rank)
        ),
        thirds AS (
            SELECT name_id, country_code, sex, MAX(n) AS n,
                   AVG(CASE WHEN rn <= max(1, n / 3) THEN rank END) AS early_avg,
                   AVG(CASE WHEN rn > n - max(1, n / 3) THEN rank END) AS recent_avg
            FROM ranked
            GROUP BY name_id, country_code, sex
        ),
        stats AS (
            SELECT a.*,
                   CASE
                       WHEN t.n IS NULL THEN NULL
                       WHEN t.n < 2 THEN 'stable'
                       WHEN t.early_avg - t.recent_avg > t.early_avg * 0.1 THEN 'rising'
                       WHEN t.early_avg - t.recent_avg < -t.early_avg * 0.1 THEN 'falling'
                       ELSE 'stable'
                   END AS trend
            FROM yr_agg a
            LEFT JOIN thirds t USING (name_id, country_code, sex)
        )"""


def _order_by(f: NameFilters) -> str:
    direction = "DESC" if f.sort_dir == "desc" else "ASC"
    if f.sort_by == "alpha":
        key = "d.name_lower"
    elif f.sort_by == "length":
        key = "d.length"
    else:
        key = f"coalesce(m.best_rank, {_UNRANKED})"
    return f"{key} {direction}, d.name_lower ASC, m.sex ASC"


def _page_keys(db: Session, f: NameFilters, sexes: list[str], countries: list[str] | None):
    """Returns (total, [(name_id, sex), ...]) for the requested page."""
    params: dict = {}
    stats = _stats_ctes(f, sexes, countries, params, with_trend=f.trend != "any")

    having = []
    if countries and f.match_mode == "all":
        having.append("COUNT(DISTINCT country_code) = :n_countries")
        params["n_countries"] = len(set(countries))
    if f.trend != "any":
        having.append("SUM(trend = :trend) > 0")
        params["trend"] = f.trend

    matched = "matched_rows"
    unisex_cte = ""
    if f.unisex_only:
        # Unisex is judged on the rows that survived every filter above, but before
        # vetoes are excluded (a veto on one sex doesn't make the other non-unisex).
        unisex_cte = """,
        unisex_rows AS (
            SELECT name_id, sex, best_rank FROM (
                SELECT *, MIN(sex) OVER (PARTITION BY name_id) AS lo_sex,
                          MAX(sex) OVER (PARTITION BY name_id) AS hi_sex
                FROM matched_rows
            )
            WHERE lo_sex <> hi_sex
        )"""
        matched = "unisex_rows"

    where = []
    if f.exclude_vetoed:
        # name_reactions has no (name_id, sex) index, so a correlated NOT EXISTS
        # rescans it per row; NOT IN builds the veto set once.
        where.append(
            "(m.name_id, m.sex) NOT IN"
            " (SELECT name_id, sex FROM name_reactions WHERE reaction = 'veto')"
        )

    base_sql = f"""
        WITH {stats},
        matched_rows AS (
            SELECT name_id, sex, MIN(best_rank) AS best_rank
            FROM stats
            GROUP BY name_id, sex
            {"HAVING " + " AND ".join(having) if having else ""}
        ){unisex_cte}
        SELECT m.name_id, m.sex, COUNT(*) OVER () AS total
        FROM {matched} m
        JOIN dim_name d ON d.id = m.name_id
        {"WHERE " + " AND ".join(where) if where else ""}
    """
    params["limit"] = f.page_size
    params["offset"] = (f.page - 1) * f.page_size
    rows = db.execute(
        text(f"{base_sql} ORDER BY {_order_by(f)} LIMIT :limit OFFSET :offset"), params
    ).all()
    if rows:
        return rows[0].total, [(r.name_id, r.sex) for r in rows]
    if params["offset"] == 0:
        return 0, []
    # Paged past the end: the window count came back with no rows, so count directly.
    total = db.execute(text(f"SELECT COUNT(*) FROM ({base_sql})"), params).scalar_one()
    return total, []


def _fetch_page_stats(
    db: Session, f: NameFilters, sexes: list[str], countries: list[str] | None, name_ids: list[int]
):
    """Returns {(name_id, sex): [stat_dict, ...]} sorted by country, for just the page's names."""
    params: dict = {}
    stats = _stats_ctes(f, sexes, countries, params, with_trend=True, page_name_ids=name_ids)
    rows = db.execute(
        text(f"WITH {stats} SELECT * FROM stats ORDER BY country_code"), params
    ).all()
    result: dict[tuple[int, str], list[dict]] = {}
    for r in rows:
        result.setdefault((r.name_id, r.sex), []).append(
            {
                "country_code": r.country_code,
                "best_rank": r.best_rank,
                "total_count": r.total_count or 0,
                "first_year": r.first_year,
                "last_year": r.last_year,
                "trend": r.trend,
            }
        )
    return result


def _fetch_reactions(db: Session, name_ids: list[int], sexes: list[str]):
    """Returns {(name_id, sex): {person_key: reaction}}."""
    result: dict[tuple[int, str], dict[str, str | None]] = {}
    if not name_ids:
        return result
    rows = (
        db.query(NameReaction.name_id, NameReaction.sex, Person.key, NameReaction.reaction)
        .join(Person, Person.id == NameReaction.person_id)
        .filter(NameReaction.name_id.in_(name_ids), NameReaction.sex.in_(sexes))
        .all()
    )
    for name_id, sex, person_key, reaction in rows:
        result.setdefault((name_id, sex), {})[person_key] = reaction
    return result


def query_names(db: Session, f: NameFilters):
    sexes = ["M", "F"] if f.sex == "ALL" else [f.sex]
    countries = sorted(set(f.countries)) if f.countries else None

    total, page_keys = _page_keys(db, f, sexes, countries)
    return total, _build_results(db, f, sexes, countries, page_keys)


def _build_results(
    db: Session,
    f: NameFilters,
    sexes: list[str],
    countries: list[str] | None,
    page_keys: list[tuple[int, str]],
) -> list[dict]:
    if not page_keys:
        return []

    # page_size is capped by the API, so these IN lists stay small.
    page_name_ids = sorted({name_id for name_id, _ in page_keys})
    names_by_id = {n.id: n for n in db.query(DimName).filter(DimName.id.in_(page_name_ids)).all()}
    stats_map = _fetch_page_stats(db, f, sexes, countries, page_name_ids)
    reactions_map = _fetch_reactions(db, page_name_ids, sexes)

    results = []
    for name_id, sex in page_keys:
        dim = names_by_id[name_id]
        reactions = {k: None for k in _all_person_keys()}
        reactions.update(reactions_map.get((name_id, sex), {}))
        results.append(
            {
                "name_id": dim.id,
                "name": dim.name,
                "sex": sex,
                "starting_letter": dim.starting_letter,
                "length": dim.length,
                "syllable_count": dim.syllable_count,
                "countries": stats_map.get((name_id, sex), []),
                "reactions": reactions,
            }
        )

    return results
