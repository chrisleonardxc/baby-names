const SIBLINGS = 2;

function range(start: number, end: number): number[] {
  const out: number[] = [];
  for (let i = start; i <= end; i++) out.push(i);
  return out;
}

function getPageNumbers(current: number, total: number): (number | "...")[] {
  const windowSize = SIBLINGS * 2 + 5; // first + last + current + siblings on both sides
  if (total <= windowSize) return range(1, total);

  const left = Math.max(2, current - SIBLINGS);
  const right = Math.min(total - 1, current + SIBLINGS);

  const pages: (number | "...")[] = [1];
  if (left > 2) pages.push("...");
  pages.push(...range(left, right));
  if (right < total - 1) pages.push("...");
  pages.push(total);
  return pages;
}

interface Props {
  page: number;
  totalPages: number;
  onChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onChange }: Props) {
  if (totalPages <= 1) return null;
  const pages = getPageNumbers(page, totalPages);

  return (
    <div className="pagination">
      <button disabled={page <= 1} onClick={() => onChange(page - 1)}>
        Previous
      </button>
      {pages.map((p, i) =>
        p === "..." ? (
          <span key={`ellipsis-${i}`} className="pagination__ellipsis">
            &hellip;
          </span>
        ) : (
          <button
            key={p}
            className={`pagination__page ${p === page ? "is-active" : ""}`}
            aria-current={p === page ? "page" : undefined}
            onClick={() => onChange(p)}
          >
            {p}
          </button>
        ),
      )}
      <button disabled={page >= totalPages} onClick={() => onChange(page + 1)}>
        Next
      </button>
    </div>
  );
}
