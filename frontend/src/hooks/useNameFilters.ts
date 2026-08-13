import { useCallback, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { DEFAULT_FILTERS, type NameFiltersState } from "../api/types";

function parseFilters(params: URLSearchParams): NameFiltersState {
  const num = (key: string): number | null => {
    const v = params.get(key);
    return v == null || v === "" ? null : Number(v);
  };
  return {
    sex: (params.get("sex") as NameFiltersState["sex"]) ?? DEFAULT_FILTERS.sex,
    unisex_only: params.get("unisex_only") === "true",
    countries: params.get("countries")?.split(",").filter(Boolean) ?? [],
    match_mode: (params.get("match_mode") as NameFiltersState["match_mode"]) ?? DEFAULT_FILTERS.match_mode,
    year_min: num("year_min"),
    year_max: num("year_max"),
    rank_max: num("rank_max"),
    starting_letter: params.get("starting_letter"),
    length_min: num("length_min"),
    length_max: num("length_max"),
    syllables_min: num("syllables_min"),
    syllables_max: num("syllables_max"),
    trend: (params.get("trend") as NameFiltersState["trend"]) ?? DEFAULT_FILTERS.trend,
    sort_by: (params.get("sort_by") as NameFiltersState["sort_by"]) ?? DEFAULT_FILTERS.sort_by,
    sort_dir: (params.get("sort_dir") as NameFiltersState["sort_dir"]) ?? DEFAULT_FILTERS.sort_dir,
    page: num("page") ?? 1,
    page_size: num("page_size") ?? DEFAULT_FILTERS.page_size,
  };
}

function filtersToParams(filters: NameFiltersState): URLSearchParams {
  const params = new URLSearchParams();
  params.set("sex", filters.sex);
  if (filters.unisex_only) params.set("unisex_only", "true");
  if (filters.countries.length) params.set("countries", filters.countries.join(","));
  if (filters.match_mode !== DEFAULT_FILTERS.match_mode) params.set("match_mode", filters.match_mode);
  if (filters.year_min != null) params.set("year_min", String(filters.year_min));
  if (filters.year_max != null) params.set("year_max", String(filters.year_max));
  if (filters.rank_max != null) params.set("rank_max", String(filters.rank_max));
  if (filters.starting_letter) params.set("starting_letter", filters.starting_letter);
  if (filters.length_min != null) params.set("length_min", String(filters.length_min));
  if (filters.length_max != null) params.set("length_max", String(filters.length_max));
  if (filters.syllables_min != null) params.set("syllables_min", String(filters.syllables_min));
  if (filters.syllables_max != null) params.set("syllables_max", String(filters.syllables_max));
  if (filters.trend !== "any") params.set("trend", filters.trend);
  if (filters.sort_by !== DEFAULT_FILTERS.sort_by) params.set("sort_by", filters.sort_by);
  if (filters.sort_dir !== DEFAULT_FILTERS.sort_dir) params.set("sort_dir", filters.sort_dir);
  if (filters.page !== 1) params.set("page", String(filters.page));
  if (filters.page_size !== DEFAULT_FILTERS.page_size) params.set("page_size", String(filters.page_size));
  return params;
}

export function useNameFilters(): [NameFiltersState, (patch: Partial<NameFiltersState>) => void] {
  const [searchParams, setSearchParams] = useSearchParams();

  // Seed the URL with friendly defaults on a bare first load only -- once any
  // param exists, an absent field (e.g. rank_max) means the user explicitly
  // cleared it to "Any", not "go back to the default".
  useEffect(() => {
    if (searchParams.size === 0) {
      setSearchParams(filtersToParams(DEFAULT_FILTERS), { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filters = useMemo(() => parseFilters(searchParams), [searchParams]);

  const updateFilters = useCallback(
    (patch: Partial<NameFiltersState>) => {
      const next = { ...filters, ...patch };
      // any filter change other than an explicit page change resets pagination
      if (!("page" in patch)) {
        next.page = 1;
      }
      setSearchParams(filtersToParams(next), { replace: true });
    },
    [filters, setSearchParams],
  );

  return [filters, updateFilters];
}
