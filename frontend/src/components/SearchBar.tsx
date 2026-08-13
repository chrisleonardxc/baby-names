import { useEffect, useState } from "react";
import type { NameFiltersState } from "../api/types";

interface Props {
  filters: NameFiltersState;
  onChange: (patch: Partial<NameFiltersState>) => void;
}

export function SearchBar({ filters, onChange }: Props) {
  const [value, setValue] = useState(filters.search ?? "");

  // Keep in sync if the filter changes from elsewhere (e.g. browser back/forward).
  useEffect(() => {
    setValue(filters.search ?? "");
  }, [filters.search]);

  // Debounce so typing doesn't fire a request per keystroke.
  useEffect(() => {
    const handle = setTimeout(() => {
      const next = value || null;
      if (next !== filters.search) {
        onChange({ search: next });
      }
    }, 300);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return (
    <div className="search-bar">
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search names…"
        aria-label="Search names"
      />
    </div>
  );
}
