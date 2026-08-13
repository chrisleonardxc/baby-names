from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy.orm import Session

from shared.config import settings
from shared.models import DimName, FactNameCountrySexAgg, FactNameYear, NameReaction, Person


@dataclass
class NameFilters:
    sex: str = "ALL"  # M | F | ALL
    unisex_only: bool = False
    countries: list[str] | None = None
    match_mode: str = "any"  # any | all
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


@dataclass
class _CountryStat:
    country_code: str
    best_rank: int | None
    total_count: int
    first_year: int | None
    last_year: int | None
    trend: str | None = None


@dataclass
class _Row:
    name_id: int
    sex: str
    countries: dict[str, _CountryStat] = field(default_factory=dict)


def _all_person_keys() -> list[str]:
    return [settings.person_a_key, settings.person_b_key]


def _fetch_stats(db: Session, sexes: list[str], countries: list[str] | None, f: NameFilters):
    """Returns list of (name_id, country_code, sex, best_rank, total_count, first_year, last_year)."""
    if f.year_min is None and f.year_max is None:
        q = db.query(
            FactNameCountrySexAgg.name_id,
            FactNameCountrySexAgg.country_code,
            FactNameCountrySexAgg.sex,
            FactNameCountrySexAgg.best_rank,
            FactNameCountrySexAgg.total_count,
            FactNameCountrySexAgg.first_year,
            FactNameCountrySexAgg.last_year,
        ).filter(FactNameCountrySexAgg.sex.in_(sexes))
        if countries:
            q = q.filter(FactNameCountrySexAgg.country_code.in_(countries))
        if f.rank_max is not None:
            q = q.filter(
                FactNameCountrySexAgg.best_rank.isnot(None),
                FactNameCountrySexAgg.best_rank <= f.rank_max,
            )
        return q.all()

    q = (
        db.query(
            FactNameYear.name_id,
            FactNameYear.country_code,
            FactNameYear.sex,
            func.min(FactNameYear.rank).label("best_rank"),
            func.sum(FactNameYear.count).label("total_count"),
            func.min(FactNameYear.year).label("first_year"),
            func.max(FactNameYear.year).label("last_year"),
        )
        .filter(FactNameYear.sex.in_(sexes))
    )
    if countries:
        q = q.filter(FactNameYear.country_code.in_(countries))
    if f.year_min is not None:
        q = q.filter(FactNameYear.year >= f.year_min)
    if f.year_max is not None:
        q = q.filter(FactNameYear.year <= f.year_max)
    q = q.group_by(FactNameYear.name_id, FactNameYear.country_code, FactNameYear.sex)
    if f.rank_max is not None:
        q = q.having(func.min(FactNameYear.rank) <= f.rank_max)
    return q.all()


def _fetch_trends(db: Session, name_ids: list[int], countries: list[str] | None, sexes: list[str]):
    if not name_ids:
        return {}
    q = db.query(
        FactNameCountrySexAgg.name_id,
        FactNameCountrySexAgg.country_code,
        FactNameCountrySexAgg.sex,
        FactNameCountrySexAgg.trend,
    ).filter(FactNameCountrySexAgg.name_id.in_(name_ids), FactNameCountrySexAgg.sex.in_(sexes))
    if countries:
        q = q.filter(FactNameCountrySexAgg.country_code.in_(countries))
    return {(r.name_id, r.country_code, r.sex): r.trend for r in q.all()}


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
    requested_countries = f.countries

    stats = _fetch_stats(db, sexes, requested_countries, f)

    grouped: dict[tuple[int, str], _Row] = {}
    for name_id, country_code, sex, best_rank, total_count, first_year, last_year in stats:
        key = (name_id, sex)
        row = grouped.setdefault(key, _Row(name_id=name_id, sex=sex))
        row.countries[country_code] = _CountryStat(
            country_code=country_code,
            best_rank=best_rank,
            total_count=total_count or 0,
            first_year=first_year,
            last_year=last_year,
        )

    if f.restrict_name_sex is not None:
        grouped = {k: v for k, v in grouped.items() if k in f.restrict_name_sex}

    if requested_countries and f.match_mode == "all":
        wanted = set(requested_countries)
        grouped = {k: v for k, v in grouped.items() if wanted.issubset(v.countries.keys())}

    name_ids = list({name_id for name_id, _ in grouped.keys()})
    trends = _fetch_trends(db, name_ids, requested_countries, sexes)
    for (name_id, sex), row in grouped.items():
        for country_code, stat in row.countries.items():
            stat.trend = trends.get((name_id, country_code, sex))

    if f.trend != "any":
        grouped = {
            k: v
            for k, v in grouped.items()
            if any(stat.trend == f.trend for stat in v.countries.values())
        }

    if f.unisex_only:
        male_names = {nid for (nid, sex) in grouped.keys() if sex == "M"}
        female_names = {nid for (nid, sex) in grouped.keys() if sex == "F"}
        both = male_names & female_names
        grouped = {k: v for k, v in grouped.items() if k[0] in both}

    name_ids = list({name_id for name_id, _ in grouped.keys()})
    if not name_ids:
        return 0, []

    names_by_id = {n.id: n for n in db.query(DimName).filter(DimName.id.in_(name_ids)).all()}

    def passes_name_filters(dim: DimName) -> bool:
        if f.starting_letter and dim.starting_letter.upper() != f.starting_letter.upper():
            return False
        if f.length_min is not None and dim.length < f.length_min:
            return False
        if f.length_max is not None and dim.length > f.length_max:
            return False
        if f.syllables_min is not None and (dim.syllable_count or 0) < f.syllables_min:
            return False
        if f.syllables_max is not None and (dim.syllable_count or 0) > f.syllables_max:
            return False
        return True

    filtered_rows = []
    for (name_id, sex), row in grouped.items():
        dim = names_by_id.get(name_id)
        if dim is None or not passes_name_filters(dim):
            continue
        filtered_rows.append((dim, sex, row))

    reactions_map = _fetch_reactions(db, [d.id for d, _, _ in filtered_rows], sexes)

    if f.exclude_vetoed:
        def is_vetoed(dim, sex):
            reactions = reactions_map.get((dim.id, sex), {})
            return any(r == "veto" for r in reactions.values())

        filtered_rows = [r for r in filtered_rows if not is_vetoed(r[0], r[1])]

    def sort_key(item):
        dim, sex, row = item
        if f.sort_by == "alpha":
            return dim.name_lower
        if f.sort_by == "length":
            return dim.length
        ranks = [s.best_rank for s in row.countries.values() if s.best_rank is not None]
        return min(ranks) if ranks else float("inf")

    reverse = f.sort_dir == "desc"
    filtered_rows.sort(key=sort_key, reverse=reverse)

    total = len(filtered_rows)
    start = (f.page - 1) * f.page_size
    page_rows = filtered_rows[start : start + f.page_size]

    results = []
    for dim, sex, row in page_rows:
        person_keys = _all_person_keys()
        reactions = {k: None for k in person_keys}
        reactions.update(reactions_map.get((dim.id, sex), {}))
        results.append(
            {
                "name_id": dim.id,
                "name": dim.name,
                "sex": sex,
                "starting_letter": dim.starting_letter,
                "length": dim.length,
                "syllable_count": dim.syllable_count,
                "countries": [
                    {
                        "country_code": s.country_code,
                        "best_rank": s.best_rank,
                        "total_count": s.total_count,
                        "first_year": s.first_year,
                        "last_year": s.last_year,
                        "trend": s.trend,
                    }
                    for s in sorted(row.countries.values(), key=lambda s: s.country_code)
                ],
                "reactions": reactions,
            }
        )

    return total, results
