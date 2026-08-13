import { useViewer } from "../context/ViewerContext";

export function ViewerToggle() {
  const { people, viewer, setViewer } = useViewer();

  if (people.length === 0) return null;

  return (
    <div className="viewer-toggle">
      <span className="viewer-toggle__label">Viewing as</span>
      <div className="viewer-toggle__pills">
        {people.map((p) => (
          <button
            key={p.key}
            className={`viewer-toggle__pill ${viewer === p.key ? "is-active" : ""}`}
            onClick={() => setViewer(p.key)}
          >
            {p.display_name}
          </button>
        ))}
      </div>
    </div>
  );
}
