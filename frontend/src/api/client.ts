import type {
  CountryMeta,
  NameDetail,
  NameFiltersState,
  NamesResponse,
  PersonMeta,
  ReactionValue,
} from "./types";

const BASE = "/api";

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getCountries(): Promise<CountryMeta[]> {
  return getJSON<CountryMeta[]>("/meta/countries");
}

export function getPeople(): Promise<PersonMeta[]> {
  return getJSON<PersonMeta[]>("/meta/people");
}

export async function checkAuthStatus(): Promise<boolean> {
  const res = await fetch(`${BASE}/auth/status`);
  return res.ok;
}

export async function login(password: string): Promise<boolean> {
  const res = await fetch(`${BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  return res.ok;
}

function filtersToQueryString(filters: NameFiltersState, extra?: Record<string, string>): string {
  const params = new URLSearchParams();
  params.set("sex", filters.sex);
  if (filters.unisex_only) params.set("unisex_only", "true");
  if (filters.countries.length) params.set("countries", filters.countries.join(","));
  params.set("match_mode", filters.match_mode);
  if (filters.search) params.set("search", filters.search);
  if (filters.year_min != null) params.set("year_min", String(filters.year_min));
  if (filters.year_max != null) params.set("year_max", String(filters.year_max));
  if (filters.rank_max != null) params.set("rank_max", String(filters.rank_max));
  if (filters.starting_letter) params.set("starting_letter", filters.starting_letter);
  if (filters.length_min != null) params.set("length_min", String(filters.length_min));
  if (filters.length_max != null) params.set("length_max", String(filters.length_max));
  if (filters.syllables_min != null) params.set("syllables_min", String(filters.syllables_min));
  if (filters.syllables_max != null) params.set("syllables_max", String(filters.syllables_max));
  if (filters.trend !== "any") params.set("trend", filters.trend);
  params.set("sort_by", filters.sort_by);
  params.set("sort_dir", filters.sort_dir);
  params.set("page", String(filters.page));
  params.set("page_size", String(filters.page_size));
  if (extra) {
    for (const [k, v] of Object.entries(extra)) params.set(k, v);
  }
  return params.toString();
}

export function getNames(filters: NameFiltersState, viewer: string | null): Promise<NamesResponse> {
  const qs = filtersToQueryString(filters, viewer ? { viewer } : undefined);
  return getJSON<NamesResponse>(`/names?${qs}`);
}

export function getFavoritesOf(
  filters: NameFiltersState,
  viewer: string | null,
  favoritedBy: string,
): Promise<NamesResponse> {
  const extra: Record<string, string> = { favorited_by: favoritedBy };
  if (viewer) extra.viewer = viewer;
  const qs = filtersToQueryString(filters, extra);
  return getJSON<NamesResponse>(`/names?${qs}`);
}

export function getShortlist(filters: NameFiltersState): Promise<NamesResponse> {
  const qs = filtersToQueryString(filters);
  return getJSON<NamesResponse>(`/shortlist?${qs}`);
}

export function getNameDetail(nameId: number, sex: "M" | "F"): Promise<NameDetail> {
  return getJSON<NameDetail>(`/names/${nameId}?sex=${sex}`);
}

export async function setReaction(
  personKey: string,
  nameId: number,
  sex: "M" | "F",
  reaction: ReactionValue,
): Promise<void> {
  const res = await fetch(`${BASE}/reactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ person_key: personKey, name_id: nameId, sex, reaction }),
  });
  if (!res.ok) {
    throw new Error(`setReaction failed: ${res.status}`);
  }
}
