"""Australian baby names, by state/territory.

Sourced from the ozbabynames project (github.com/robjhyndman/ozbabynames), which
itself stitches together each state/territory's births-registry publications --
coverage and years vary a lot by state (South Australia has full counts back to
1944; others are recent top-100-only lists). There's no single national total, so
each state is ingested as its own region under country_code="AU"; the app's
per-country aggregate rolls them up.

Tasmania is not included: its raw files are a handful of inconsistently-shaped
spreadsheets covering only 2010-2016, not worth the parsing complexity for the
data volume gained. Add it the same way as the others below if that changes.

Reads from vendored snapshots in ingestion/vendored/au/ -- see
ingestion/vendored/PROVENANCE.md. To refresh: re-download the CSVs linked there.
"""

import csv
import logging
from pathlib import Path

from ingestion.common.schema import NormalizedNameRecord

logger = logging.getLogger("ingestion.au_ozbabynames")

SOURCE = "ozbabynames"
VENDORED_DIR = Path(__file__).resolve().parent.parent / "vendored" / "au"

SEX_MAP = {"Male": "M", "Female": "F"}


def _read_csv(filename: str, count_col: str) -> list[tuple[str, str, int, int]]:
    """Returns [(name, sex, year, count), ...]."""
    path = VENDORED_DIR / filename
    rows = []
    with open(path, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            sex = SEX_MAP.get((row.get("sex") or "").strip())
            year_raw = (row.get("year") or "").strip()
            count_raw = (row.get(count_col) or "").strip()
            if not name or not sex or not year_raw or not count_raw:
                continue
            try:
                year = int(float(year_raw))
                count = int(float(count_raw))
            except ValueError:
                continue
            rows.append((name.title(), sex, year, count))
    return rows


def _read_qld_2024_wide(filename: str) -> list[tuple[str, str, int, int]]:
    path = VENDORED_DIR / filename
    rows = []
    with open(path, encoding="latin-1", newline="") as f:
        for row in csv.DictReader(f):
            girl, girl_count = row.get("Girl Names"), row.get("Count of Girl Names")
            boy, boy_count = row.get("Boy Names"), row.get("Count of Boy Names")
            if girl and girl_count:
                rows.append((girl.strip().title(), "F", 2024, int(float(girl_count))))
            if boy and boy_count:
                rows.append((boy.strip().title(), "M", 2024, int(float(boy_count))))
    return rows


STATE_READERS: dict[str, list[tuple[str, str]]] = {
    "NSW": [("nsw.csv", "number")],
    "NT": [("nt.csv", "number")],
    "QLD": [("qld.csv", "number")],
    "SA": [("sa.csv", "number")],
    "VIC": [("vic.csv", "number")],
    "WA": [("wa.csv", "count")],
}


def _with_computed_rank(rows: list[tuple[str, str, int, int]], state: str) -> list[NormalizedNameRecord]:
    groups: dict[tuple[str, int], list[tuple[str, int]]] = {}
    for name, sex, year, count in rows:
        groups.setdefault((sex, year), []).append((name, count))

    records = []
    for (sex, year), name_counts in groups.items():
        name_counts.sort(key=lambda nc: -nc[1])
        for rank, (name, count) in enumerate(name_counts, start=1):
            records.append(
                NormalizedNameRecord(
                    name=name,
                    sex=sex,
                    year=year,
                    country_code="AU",
                    source=SOURCE,
                    count=count,
                    rank=rank,
                    region_code=state,
                )
            )
    return records


def fetch_records() -> list[NormalizedNameRecord]:
    all_records: list[NormalizedNameRecord] = []

    for state, files in STATE_READERS.items():
        raw_rows: list[tuple[str, str, int, int]] = []
        for filename, count_col in files:
            try:
                raw_rows.extend(_read_csv(filename, count_col))
            except Exception:
                logger.exception("failed to read %s for state=%s", filename, state)
        if state == "QLD":
            try:
                raw_rows.extend(_read_qld_2024_wide("qld_2024.csv"))
            except Exception:
                logger.exception("failed to read qld_2024.csv")

        records = _with_computed_rank(raw_rows, state)
        logger.info("parsed %d AU records for state=%s", len(records), state)
        all_records.extend(records)

    return all_records
