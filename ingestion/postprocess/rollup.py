import logging

from sqlalchemy.orm import Session

from shared.models import FactNameCountrySexAgg, FactNameYear

logger = logging.getLogger("ingestion.rollup")


def _compute_trend(years_ranks: list[tuple[int, int]]) -> tuple[str, float]:
    """years_ranks: [(year, rank), ...] sorted by year, rank lower = more popular.
    Compares the average rank of the earliest third of years vs the latest third.
    A lower (better) recent rank than earlier => rising; higher => falling.
    """
    if len(years_ranks) < 2:
        return "stable", 0.0

    n = len(years_ranks)
    third = max(1, n // 3)
    early = years_ranks[:third]
    recent = years_ranks[-third:]
    early_avg = sum(r for _, r in early) / len(early)
    recent_avg = sum(r for _, r in recent) / len(recent)

    slope = early_avg - recent_avg  # positive => rank improved (rising popularity)
    if slope > early_avg * 0.1:
        return "rising", slope
    if slope < -early_avg * 0.1:
        return "falling", slope
    return "stable", slope


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
        trend, slope = _compute_trend(years_ranks)

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
