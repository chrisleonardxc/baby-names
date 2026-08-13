import { useState } from "react";
import { getFavoritesOf } from "../api/client";
import { FilterPanel } from "../components/FilterPanel";
import { NameDetailModal } from "../components/NameDetailModal";
import { ResultsGrid } from "../components/ResultsGrid";
import { SearchBar } from "../components/SearchBar";
import { useViewer } from "../context/ViewerContext";
import { useNameFilters } from "../hooks/useNameFilters";

export function FavoritesPage() {
  const [filters, updateFilters] = useNameFilters();
  const { people, viewer } = useViewer();
  const [whoseFavorites, setWhoseFavorites] = useState<string | null>(null);
  const [detail, setDetail] = useState<{ nameId: number; sex: "M" | "F" } | null>(null);

  const effectiveWhose = whoseFavorites ?? viewer;
  if (!effectiveWhose) return null;

  return (
    <>
      <SearchBar filters={filters} onChange={updateFilters} />
      <div className="page">
      <div className="page__toggle-row">
        {people.map((p) => (
          <button
            key={p.key}
            className={`page__toggle ${effectiveWhose === p.key ? "is-active" : ""}`}
            onClick={() => setWhoseFavorites(p.key)}
          >
            {p.key === viewer ? "My Favorites" : `${p.display_name}'s Favorites`}
          </button>
        ))}
      </div>
      <p className="page__hint">
        {effectiveWhose === viewer
          ? "Names you've favorited."
          : "Names they've favorited — favorite or veto any of them yourself right here."}
      </p>
      <FilterPanel filters={filters} onChange={updateFilters} />
      <ResultsGrid
        filters={filters}
        fetcher={(f) => getFavoritesOf(f, viewer, effectiveWhose)}
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
