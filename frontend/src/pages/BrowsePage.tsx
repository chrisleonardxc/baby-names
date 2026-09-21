import { useCallback, useState } from "react";
import { getNames } from "../api/client";
import type { NameFiltersState } from "../api/types";
import { FilterPanel } from "../components/FilterPanel";
import { NameDetailModal } from "../components/NameDetailModal";
import { ResultsGrid } from "../components/ResultsGrid";
import { SearchBar } from "../components/SearchBar";
import { useViewer } from "../context/ViewerContext";
import { useNameFilters } from "../hooks/useNameFilters";

export function BrowsePage() {
  const [filters, updateFilters] = useNameFilters();
  const { viewer } = useViewer();
  const [detail, setDetail] = useState<{ nameId: number; sex: "M" | "F" } | null>(null);
  // Stable identity: ResultsGrid refetches whenever its fetcher changes.
  const fetcher = useCallback(
    (f: NameFiltersState, signal: AbortSignal) => getNames(f, viewer, signal),
    [viewer],
  );

  return (
    <>
      <SearchBar filters={filters} onChange={updateFilters} />
      <div className="page">
        <FilterPanel filters={filters} onChange={updateFilters} />
        <ResultsGrid
          filters={filters}
          fetcher={fetcher}
          onChangePage={(page) => updateFilters({ page })}
          onOpenDetail={(nameId, sex) => setDetail({ nameId, sex })}
        />
        {detail && (
          <NameDetailModal nameId={detail.nameId} sex={detail.sex} onClose={() => setDetail(null)} />
        )}
      </div>
    </>
  );
}
