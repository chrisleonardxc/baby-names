export interface CountryMeta {
  country_code: string;
  display_name: string;
  min_year: number | null;
  max_year: number | null;
}

export interface PersonMeta {
  key: string;
  display_name: string;
}

export interface CountryStat {
  country_code: string;
  best_rank: number | null;
  total_count: number;
  first_year: number | null;
  last_year: number | null;
  trend: string | null;
}

export type ReactionValue = "favorite" | "veto" | null;

export interface NameResult {
  name_id: number;
  name: string;
  sex: "M" | "F";
  starting_letter: string;
  length: number;
  syllable_count: number | null;
  countries: CountryStat[];
  reactions: Record<string, ReactionValue>;
}

export interface NamesResponse {
  total: number;
  page: number;
  page_size: number;
  results: NameResult[];
}

export interface YearPoint {
  country_code: string;
  year: number;
  count: number | null;
  rank: number | null;
}

export interface NameDetail {
  name_id: number;
  name: string;
  sex: "M" | "F";
  timeseries: YearPoint[];
  reactions: Record<string, ReactionValue>;
}

export interface NameFiltersState {
  sex: "M" | "F" | "ALL";
  unisex_only: boolean;
  countries: string[];
  match_mode: "any" | "all";
  search: string | null;
  year_min: number | null;
  year_max: number | null;
  rank_max: number | null;
  starting_letter: string | null;
  length_min: number | null;
  length_max: number | null;
  syllables_min: number | null;
  syllables_max: number | null;
  trend: "rising" | "falling" | "stable" | "any";
  sort_by: "popularity" | "alpha" | "length";
  sort_dir: "asc" | "desc";
  page: number;
  page_size: number;
}

export const DEFAULT_FILTERS: NameFiltersState = {
  sex: "ALL",
  unisex_only: false,
  countries: [],
  match_mode: "any",
  search: null,
  year_min: null,
  year_max: null,
  rank_max: 500,
  starting_letter: null,
  length_min: null,
  length_max: null,
  syllables_min: null,
  syllables_max: null,
  trend: "any",
  sort_by: "popularity",
  sort_dir: "asc",
  page: 1,
  page_size: 30,
};
