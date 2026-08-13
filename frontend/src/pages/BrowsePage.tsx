import { useState } from "react";
import { getNames } from "../api/client";
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

  return (
    <>
      <SearchBar filters={filters} onChange={updateFilters} />
      <div className="page">
        <FilterPanel filters={filters} onChange={updateFilters} />
        <ResultsGrid
          filters={filters}
          fetcher={(f) => getNames(f, viewer)}
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
