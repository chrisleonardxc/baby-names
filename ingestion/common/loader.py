import logging

from sqlalchemy.orm import Session

from ingestion.common.heuristics import estimate_syllables
from ingestion.common.schema import NormalizedNameRecord
from shared.models import DimName, FactNameYear

logger = logging.getLogger("ingestion.loader")


def _dedupe(records: list[NormalizedNameRecord]) -> list[NormalizedNameRecord]:
    """Collapse any records sharing a unique-constraint key, summing counts / keeping best rank."""
    merged: dict[tuple, NormalizedNameRecord] = {}
    for rec in records:
        key = (rec.name.lower(), rec.country_code, rec.region_code, rec.sex, rec.year, rec.source)
        existing = merged.get(key)
        if existing is None:
            merged[key] = rec
            continue
        combined_count = (existing.count or 0) + (rec.count or 0)
        best_rank = min([r for r in (existing.rank, rec.rank) if r is not None], default=None)
        merged[key] = NormalizedNameRecord(
            name=existing.name,
            sex=existing.sex,
            year=existing.year,
            country_code=existing.country_code,
            source=existing.source,
            count=combined_count or None,
            rank=best_rank,
            region_code=existing.region_code,
        )
    return list(merged.values())


def _get_or_create_name_id(session: Session, cache: dict[str, int], name: str) -> int:
    key = name.lower()
    if key in cache:
        return cache[key]
    dim = session.query(DimName).filter(DimName.name_lower == key).one_or_none()
    if dim is None:
        dim = DimName(
            name=name,
            name_lower=key,
            length=len(name),
            starting_letter=name[0].upper(),
            syllable_count=estimate_syllables(name),
        )
        session.add(dim)
        session.flush()
    cache[key] = dim.id
    return dim.id


def load_records(session: Session, country_code: str, source: str, records: list[NormalizedNameRecord]) -> int:
    """Idempotently replace all fact rows for (country_code, source) with the given records."""
    deleted = (
        session.query(FactNameYear)
        .filter(FactNameYear.country_code == country_code, FactNameYear.source == source)
        .delete(synchronize_session=False)
    )
    logger.info("cleared %d existing rows for country=%s source=%s", deleted, country_code, source)

    deduped = _dedupe(records)
    name_id_cache: dict[str, int] = {}
    rows = []
    for rec in deduped:
        name_id = _get_or_create_name_id(session, name_id_cache, rec.name)
        rows.append(
            FactNameYear(
                name_id=name_id,
                country_code=rec.country_code,
                region_code=rec.region_code,
                sex=rec.sex,
                year=rec.year,
                count=rec.count,
                rank=rec.rank,
                source=rec.source,
            )
        )

    session.bulk_save_objects(rows)
    session.commit()
    logger.info("loaded %d rows for country=%s source=%s", len(rows), country_code, source)
    return len(rows)
