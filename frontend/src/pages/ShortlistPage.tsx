import { useState } from "react";
import { getShortlist } from "../api/client";
import { FilterPanel } from "../components/FilterPanel";
import { NameDetailModal } from "../components/NameDetailModal";
import { ResultsGrid } from "../components/ResultsGrid";
import { useNameFilters } from "../hooks/useNameFilters";

export function ShortlistPage() {
  const [filters, updateFilters] = useNameFilters();
  const [detail, setDetail] = useState<{ nameId: number; sex: "M" | "F" } | null>(null);

  return (
    <div className="page">
      <p className="page__hint">Names you both favorited, and neither of you vetoed.</p>
      <FilterPanel filters={filters} onChange={updateFilters} />
      <ResultsGrid
        filters={filters}
        fetcher={getShortlist}
        onChangePage={(page) => updateFilters({ page })}
        onOpenDetail={(nameId, sex) => setDetail({ nameId, sex })}
      />
      {detail && (
        <NameDetailModal nameId={detail.nameId} sex={detail.sex} onClose={() => setDetail(null)} />
      )}
    </div>
  );
}
