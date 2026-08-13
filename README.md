# Baby Name Finder

A self-hosted app for browsing baby-name popularity data (by sex, country, year, and
more) with sliders/filters, plus a shared favorite/veto shortlist for two people.

## Stack

- **Backend:** FastAPI + SQLAlchemy, SQLite (file-based, no separate DB container)
- **Ingestion:** standalone Python ETL that loads open government name datasets into
  the same SQLite database that the API reads from. All source data lives in
  `ingestion/vendored/` inside the repo — ingestion never makes a network call, see
  "Data ingestion" below.
- **Frontend:** React (Vite) + TypeScript, served in production by Nginx
- **Data sources implemented:** US (SSA, national, 1880-2025), UK (ONS, England &
  Wales, 2019-2025), Australia (per-state, coverage varies 1930/1944-2024), Canada
  (Alberta only, 1980-2024). See `ingestion/sources/` to add more (France/INSEE,
  Ireland/CSO, other Canadian provinces were scoped in the plan but not yet built).

## Running it

```bash
cp .env.example .env   # edit PERSON_A_NAME / PERSON_B_NAME if you don't want Chris/Sydney
docker compose up --build -d
make seed               # one-time: loads all four countries (~3 min)
```

Then open http://localhost:8080 (frontend) — it proxies `/api` to the backend
automatically. The bare API is also reachable directly at http://localhost:8000 for
debugging.

To (re-)load just one country without touching the others:
```bash
make seed-country COUNTRY=au   # or gb, us, ca_ab
```

## Deploying elsewhere (e.g. a home server)

Nothing in the compose file or code hardcodes a host or path. Copy `.env.example` to
`.env` on the target machine, set `DATA_DIR` to wherever you want the SQLite file to
live persistently, and run the same `docker compose up --build -d` + `make seed`.

## Data ingestion

Every dataset (US, UK, Australia, Canada/Alberta) is committed to the repo under
`ingestion/vendored/` (~28MB total). `make seed` reads those files directly into
SQLite — no network access is required to seed or run the app.

Getting *new* years of data means manually fetching the relevant file(s) and
replacing them in `ingestion/vendored/`. Each source's exact provenance, license, and
refresh instructions are in `ingestion/vendored/PROVENANCE.md`. Re-running ingestion
for a given `(country, source)` is idempotent — it fully replaces that scope's rows
rather than appending, so re-seeding never duplicates data.

## Schema

`Base.metadata.create_all()` runs on API startup — there are no Alembic migrations.
If the schema needs to evolve after real data/favorites exist, introduce Alembic at
that point (the SQLAlchemy models in `shared/models.py` are structured for it).

## SQLite journal mode

`shared/db.py` sets `PRAGMA journal_mode=DELETE` (SQLite's default) instead of WAL.
WAL's shared-memory (`-shm`) file needs real `mmap` semantics, which break under
Docker Desktop's virtualized bind mounts on macOS and can corrupt the database
("database disk image is malformed"). Don't switch this back to WAL.

## Project layout

```
baby-names/
├── docker-compose.yml   .env.example   Makefile
├── shared/              # SQLAlchemy models + config, used by both backend and ingestion
├── backend/             # FastAPI app
├── ingestion/           # ETL: common/, sources/ (one module per country), vendored/, postprocess/
└── frontend/            # React app
```
