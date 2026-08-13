# Vendored data snapshots

All ingestion reads from these committed files, not live downloads. The full dataset
across all four countries is ~28MB, small enough to just check into the repo -- this
also means the running app has zero dependency on any external network access.
Refreshing any of these means re-fetching manually and replacing the file(s); there's
no automated refresh step, by design (keeps ingestion 100% offline and deterministic).

## us/names.zip

- Source: https://www.ssa.gov/oact/babynames/names.zip
- Fetched: 2026-08-07
- Contains: US national baby name counts, 1880-2025 (yobYYYY.txt files)
- License: public domain (US government work)
- Why vendored: ssa.gov sits behind bot protection that returns 403 for
  curl/requests-style clients regardless of User-Agent or headers -- only a real
  browser TLS/HTTP fingerprint gets through. Fetched via a real browser session.

## gb/{year}_{sex}.xlsx (14 files, 2019-2025)

- Source: ons.gov.uk baby names for England & Wales, boys/girls, per year. ONS
  renames these files unpredictably each release (no stable URL pattern), so there
  was never going to be a live-fetch path here anyway.
- Fetched: 2026-08-07
- License: Open Government Licence v3.0 (UK)
- To add a year: download that year's boys/girls XLSX from ons.gov.uk and save as
  `{year}_M.xlsx` / `{year}_F.xlsx`.

## au/*.csv (nsw, nt, qld [+ qld_2024], sa, vic, wa)

- Source: github.com/robjhyndman/ozbabynames `data-raw/` combined per-state CSVs,
  which themselves stitch together each state/territory's births-registry releases.
  Coverage is uneven by design of the underlying sources (South Australia has full
  counts back to 1944; others are recent top-N lists only). Tasmania is excluded --
  its raw files are a handful of inconsistently-shaped spreadsheets covering only
  2010-2016, not worth the parsing complexity for the data gained.
- Fetched: 2026-08-08
- License: see github.com/robjhyndman/ozbabynames (state/territory government data,
  redistributed by that project)
- To refresh: re-download the CSVs linked from that repo's `data-raw/` folder.

## ca/ab_1980_2020.xlsx, ca/ab_2021_2024.xlsx

- Source: Service Alberta open data ("Frequency and ranking of baby names by year
  and gender"), open.alberta.ca
- Fetched: 2026-08-08
- License: Open Government Licence - Alberta
- Only Alberta is included. BC publishes similar CSVs
  (www2.gov.bc.ca/assets/.../bc-popular-{boys,girls}-names.csv) but its server closed
  the connection with no response for every fetch method tried (curl with several
  header/HTTP-version combinations, a direct fetch, and a sandboxed browser
  navigation) -- worth retrying from a different network if BC data matters later.
  There's no single federal Canadian dataset, so more provinces would each need their
  own source module the same shape as `ingestion/sources/ca_provinces/ab.py`.
