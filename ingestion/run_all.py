import argparse
import logging

from ingestion.common.loader import load_records
from ingestion.postprocess.rollup import rebuild_aggregates
from ingestion.sources import au_ozbabynames, uk_ons, us_ssa
from ingestion.sources.ca_provinces import ab as ca_ab
from shared.db import SessionLocal, init_db
from shared.seed import seed_countries, seed_people

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion.run_all")

# key -> (country_code, source, fetch_fn). Countries without an implemented module yet
# (fr, ie, and any Canadian province beyond Alberta) are intentionally absent -- see
# plan Phase 2/3 and ingestion/vendored/PROVENANCE.md.
SOURCE_MODULES = {
    "us": ("US", us_ssa.SOURCE, us_ssa.fetch_records),
    "gb": ("GB", uk_ons.SOURCE, uk_ons.fetch_records),
    "au": ("AU", au_ozbabynames.SOURCE, au_ozbabynames.fetch_records),
    "ca_ab": ("CA", ca_ab.SOURCE, ca_ab.fetch_records),
}


def run(source_keys: list[str]) -> None:
    init_db()
    session = SessionLocal()
    try:
        seed_countries(session)
        seed_people(session)

        for key in source_keys:
            if key not in SOURCE_MODULES:
                logger.warning("skipping unknown/unimplemented source key: %s", key)
                continue
            country_code, source, fetch_fn = SOURCE_MODULES[key]
            try:
                logger.info("fetching records for %s (%s)", key, source)
                records = fetch_fn()
                load_records(session, country_code, source, records)
            except Exception:
                logger.exception("ingestion failed for source=%s -- continuing with others", key)

        rebuild_aggregates(session)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest open baby-name datasets")
    parser.add_argument("--sources", type=str, default="", help="comma-separated source keys, e.g. us,gb")
    parser.add_argument("--all", action="store_true", help="ingest every implemented source")
    args = parser.parse_args()

    if args.all:
        keys = list(SOURCE_MODULES.keys())
    else:
        keys = [k.strip() for k in args.sources.split(",") if k.strip()]

    if not keys:
        parser.error("specify --sources <keys> or --all")

    run(keys)


if __name__ == "__main__":
    main()
