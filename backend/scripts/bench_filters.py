"""Time /api/names queries for a spread of filter combinations against a seeded DB.

Usage (from the repo root, against the running stack's database):
    docker compose exec api python scripts/bench_filters.py

or locally:
    DATABASE_URL=sqlite:///path/to/baby_names.db PYTHONPATH=.:backend python backend/scripts/bench_filters.py
"""

import time

from app.services.names_query import NameFilters, query_names
from shared.db import SessionLocal

CASES = {
    "default (US, top 500)": dict(countries=["US"], rank_max=500),
    "all countries, top 500": dict(rank_max=500),
    "all countries, any rank": dict(),
    "US, any rank": dict(countries=["US"]),
    "top 500, last 20 yrs": dict(rank_max=500, year_min=2006, year_max=2025),
    "US top 500, last 20 yrs": dict(countries=["US"], rank_max=500, year_min=2006, year_max=2025),
    "top 500, last 20 yrs, rising": dict(rank_max=500, year_min=2006, year_max=2025, trend="rising"),
    "top 500, rising": dict(rank_max=500, trend="rising"),
    "unisex top 100, 2000-2010": dict(rank_max=100, unisex_only=True, year_min=2000, year_max=2010),
    "top 1000, hide vetoed, by length": dict(rank_max=1000, exclude_vetoed=True, sort_by="length"),
    "search 'ann', A-Z desc": dict(search="ann", sort_by="alpha", sort_dir="desc"),
    "any rank, 1900-2025": dict(year_min=1900, year_max=2025),
    "any rank, last 20 yrs, falling": dict(year_min=2006, year_max=2025, trend="falling"),
}


def main() -> None:
    for label, kwargs in CASES.items():
        db = SessionLocal()
        try:
            start = time.perf_counter()
            total, _ = query_names(db, NameFilters(page_size=30, page=2, **kwargs))
            elapsed = time.perf_counter() - start
            print(f"{label:36s} {elapsed:6.2f}s  total={total}")
        finally:
            db.close()


if __name__ == "__main__":
    main()
