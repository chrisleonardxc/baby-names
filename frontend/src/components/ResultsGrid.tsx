import { useEffect, useState } from "react";
import type { NameFiltersState, NamesResponse, ReactionValue } from "../api/types";
import { NameCard } from "./NameCard";

interface Props {
  filters: NameFiltersState;
  fetcher: (filters: NameFiltersState) => Promise<NamesResponse>;
  onChangePage: (page: number) => void;
  onOpenDetail: (nameId: number, sex: "M" | "F") => void;
}

export function ResultsGrid({ filters, fetcher, onChangePage, onOpenDetail }: Props) {
  const [data, setData] = useState<NamesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetcher(filters)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filters), fetcher]);

  const handleReactionChange = (
    nameId: number,
    sex: "M" | "F",
    personKey: string,
    reaction: ReactionValue,
  ) => {
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        results: prev.results.map((r) =>
          r.name_id === nameId && r.sex === sex
            ? { ...r, reactions: { ...r.reactions, [personKey]: reaction } }
            : r,
        ),
      };
    });
  };

  if (loading && !data) return <div className="results-grid__status">Loading names&hellip;</div>;
  if (error) return <div className="results-grid__status results-grid__status--error">{error}</div>;
  if (!data || data.results.length === 0) {
    return (
      <div>
        {loading && <div className="results-grid__loading-banner">Updating&hellip;</div>}
        <div className="results-grid__status">No names match these filters yet.</div>
      </div>
    );
  }

  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));

  return (
    <div>
      <div className="results-grid__summary">
        {data.total} names
        {loading && <span className="results-grid__spinner" aria-label="Loading" />}
      </div>
      <div className={`results-grid ${loading ? "is-loading" : ""}`}>
        {data.results.map((r) => (
          <NameCard
            key={`${r.name_id}-${r.sex}`}
            result={r}
            onReactionChange={handleReactionChange}
            onOpenDetail={onOpenDetail}
          />
        ))}
      </div>
      {totalPages > 1 && (
        <div className="results-grid__pagination">
          <button disabled={data.page <= 1} onClick={() => onChangePage(data.page - 1)}>
            Previous
          </button>
          <span>
            Page {data.page} of {totalPages}
          </span>
          <button disabled={data.page >= totalPages} onClick={() => onChangePage(data.page + 1)}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
