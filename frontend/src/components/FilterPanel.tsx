import { useEffect, useState } from "react";
import { getCountries } from "../api/client";
import type { CountryMeta, NameFiltersState } from "../api/types";

const RANK_PRESETS = [10, 50, 100, 500, 1000];
const ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

interface Props {
  filters: NameFiltersState;
  onChange: (patch: Partial<NameFiltersState>) => void;
}

export function FilterPanel({ filters, onChange }: Props) {
  const [countries, setCountries] = useState<CountryMeta[]>([]);

  useEffect(() => {
    getCountries().then(setCountries);
  }, []);

  const yearBounds = countries.reduce(
    (acc, c) => ({
      min: c.min_year != null ? Math.min(acc.min, c.min_year) : acc.min,
      max: c.max_year != null ? Math.max(acc.max, c.max_year) : acc.max,
    }),
    { min: 9999, max: 0 },
  );

  const toggleCountry = (code: string) => {
    const set = new Set(filters.countries);
    if (set.has(code)) set.delete(code);
    else set.add(code);
    onChange({ countries: Array.from(set) });
  };

  return (
    <div className="filter-panel">
      <div className="filter-panel__group">
        <label>Sex</label>
        <div className="filter-panel__seg">
          {(["ALL", "M", "F"] as const).map((s) => (
            <button
              key={s}
              className={filters.sex === s ? "is-active" : ""}
              onClick={() => onChange({ sex: s })}
            >
              {s === "ALL" ? "All" : s === "M" ? "Boy" : "Girl"}
            </button>
          ))}
        </div>
        <label className="filter-panel__checkbox">
          <input
            type="checkbox"
            checked={filters.unisex_only}
            onChange={(e) => onChange({ unisex_only: e.target.checked })}
          />
          Unisex names only
        </label>
      </div>

      <div className="filter-panel__group">
        <label>Country</label>
        <div className="filter-panel__chips">
          {countries.map((c) => (
            <button
              key={c.country_code}
              className={filters.countries.includes(c.country_code) ? "is-active" : ""}
              onClick={() => toggleCountry(c.country_code)}
            >
              {c.display_name}
            </button>
          ))}
        </div>
        {filters.countries.length > 1 && (
          <div className="filter-panel__seg">
            {(["any", "all"] as const).map((m) => (
              <button
                key={m}
                className={filters.match_mode === m ? "is-active" : ""}
                onClick={() => onChange({ match_mode: m })}
              >
                Popular in {m === "any" ? "any selected country" : "every selected country"}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="filter-panel__group">
        <label>Popularity (top N by rank)</label>
        <div className="filter-panel__chips">
          {RANK_PRESETS.map((r) => (
            <button
              key={r}
              className={filters.rank_max === r ? "is-active" : ""}
              onClick={() => onChange({ rank_max: r })}
            >
              Top {r}
            </button>
          ))}
          <button
            className={filters.rank_max == null ? "is-active" : ""}
            onClick={() => onChange({ rank_max: null })}
          >
            Any
          </button>
        </div>
      </div>

      {yearBounds.max > 0 && (
        <div className="filter-panel__group">
          <label>
            Year range: {filters.year_min ?? yearBounds.min} &ndash; {filters.year_max ?? yearBounds.max}
          </label>
          <div className="filter-panel__range">
            <input
              type="range"
              min={yearBounds.min}
              max={yearBounds.max}
              value={filters.year_min ?? yearBounds.min}
              onChange={(e) => onChange({ year_min: Number(e.target.value) })}
            />
            <input
              type="range"
              min={yearBounds.min}
              max={yearBounds.max}
              value={filters.year_max ?? yearBounds.max}
              onChange={(e) => onChange({ year_max: Number(e.target.value) })}
            />
          </div>
        </div>
      )}

      <div className="filter-panel__group">
        <label>Starting letter</label>
        <div className="filter-panel__chips filter-panel__chips--wrap">
          <button
            className={!filters.starting_letter ? "is-active" : ""}
            onClick={() => onChange({ starting_letter: null })}
          >
            Any
          </button>
          {ALPHABET.map((letter) => (
            <button
              key={letter}
              className={filters.starting_letter === letter ? "is-active" : ""}
              onClick={() => onChange({ starting_letter: letter })}
            >
              {letter}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-panel__group">
        <label>
          Length: {filters.length_min ?? 2}&ndash;{filters.length_max ?? 15} letters
        </label>
        <div className="filter-panel__range">
          <input
            type="range"
            min={2}
            max={15}
            value={filters.length_min ?? 2}
            onChange={(e) => onChange({ length_min: Number(e.target.value) })}
          />
          <input
            type="range"
            min={2}
            max={15}
            value={filters.length_max ?? 15}
            onChange={(e) => onChange({ length_max: Number(e.target.value) })}
          />
        </div>
      </div>

      <div className="filter-panel__group">
        <label>Trend</label>
        <div className="filter-panel__seg">
          {(["any", "rising", "stable", "falling"] as const).map((t) => (
            <button
              key={t}
              className={filters.trend === t ? "is-active" : ""}
              onClick={() => onChange({ trend: t })}
            >
              {t === "any" ? "Any" : t[0].toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-panel__group">
        <label>Sort by</label>
        <div className="filter-panel__seg">
          {(["popularity", "alpha", "length"] as const).map((s) => (
            <button
              key={s}
              className={filters.sort_by === s ? "is-active" : ""}
              onClick={() => onChange({ sort_by: s })}
            >
              {s === "popularity" ? "Popularity" : s === "alpha" ? "A-Z" : "Length"}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
