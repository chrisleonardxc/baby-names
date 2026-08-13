"""US national baby names, from the Social Security Administration.

Reads from a vendored snapshot rather than downloading live -- see
ingestion/vendored/PROVENANCE.md for why (ssa.gov blocks non-browser HTTP clients
outright) and how to refresh it.
"""

import logging
import re
import zipfile
from pathlib import Path

from ingestion.common.schema import NATIONAL, NormalizedNameRecord

logger = logging.getLogger("ingestion.us_ssa")

SOURCE = "ssa_national"
VENDORED_ZIP = Path(__file__).resolve().parent.parent / "vendored" / "us" / "names.zip"

_YEAR_FILE_RE = re.compile(r"yob(\d{4})\.txt")


def fetch_records() -> list[NormalizedNameRecord]:
    records: list[NormalizedNameRecord] = []

    with zipfile.ZipFile(VENDORED_ZIP) as zf:
        for filename in zf.namelist():
            match = _YEAR_FILE_RE.match(filename)
            if not match:
                continue
            year = int(match.group(1))

            rows_by_sex: dict[str, list[tuple[str, int]]] = {"M": [], "F": []}
            with zf.open(filename) as f:
                for raw_line in f.read().decode("utf-8").splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    name, sex, count_str = line.split(",")
                    rows_by_sex[sex].append((name, int(count_str)))

            for sex, rows in rows_by_sex.items():
                rows.sort(key=lambda r: -r[1])
                for rank, (name, count) in enumerate(rows, start=1):
                    records.append(
                        NormalizedNameRecord(
                            name=name,
                            sex=sex,
                            year=year,
                            country_code="US",
                            source=SOURCE,
                            count=count,
                            rank=rank,
                            region_code=NATIONAL,
                        )
                    )

    logger.info("parsed %d SSA national records", len(records))
    return records
