import logging

from sqlalchemy.orm import Session

from shared.models import FactNameCountrySexAgg, FactNameYear
from shared.trend import compute_trend

logger = logging.getLogger("ingestion.rollup")


def rebuild_aggregates(session: Session) -> int:
    logger.info("rebuilding fact_name_country_sex_agg")
    session.query(FactNameCountrySexAgg).delete(synchronize_session=False)
    session.commit()

    rows = (
        session.query(
            FactNameYear.name_id,
            FactNameYear.country_code,
            FactNameYear.sex,
            FactNameYear.year,
            FactNameYear.rank,
            FactNameYear.count,
        )
        .order_by(FactNameYear.name_id, FactNameYear.country_code, FactNameYear.sex, FactNameYear.year)
        .all()
    )

    groups: dict[tuple[int, str, str], list[tuple[int, int | None, int | None]]] = {}
    for name_id, country_code, sex, year, rank, count in rows:
        groups.setdefault((name_id, country_code, sex), []).append((year, rank, count))

    agg_rows = []
    for (name_id, country_code, sex), entries in groups.items():
        entries.sort(key=lambda e: e[0])
        years = [e[0] for e in entries]
        ranks = [e[1] for e in entries if e[1] is not None]
        counts = [e[2] or 0 for e in entries]

        best_rank = min(ranks) if ranks else None
        total_count = sum(counts)
        first_year, last_year = years[0], years[-1]

        years_ranks = [(e[0], e[1]) for e in entries if e[1] is not None]
        trend, slope = compute_trend(years_ranks)

        agg_rows.append(
            FactNameCountrySexAgg(
                name_id=name_id,
                country_code=country_code,
                sex=sex,
                best_rank=best_rank,
                total_count=total_count,
                first_year=first_year,
                last_year=last_year,
                trend=trend,
                trend_slope=slope,
            )
        )

    session.bulk_save_objects(agg_rows)
    session.commit()
    logger.info("rebuilt %d aggregate rows", len(agg_rows))
    return len(agg_rows)
