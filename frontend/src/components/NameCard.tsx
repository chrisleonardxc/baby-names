import { useState } from "react";
import { setReaction } from "../api/client";
import type { NameResult, ReactionValue } from "../api/types";
import { useViewer } from "../context/ViewerContext";

const TREND_ICON: Record<string, string> = { rising: "↑", falling: "↓", stable: "→" };

interface Props {
  result: NameResult;
  onReactionChange: (nameId: number, sex: "M" | "F", personKey: string, reaction: ReactionValue) => void;
  onOpenDetail: (nameId: number, sex: "M" | "F") => void;
}

export function NameCard({ result, onReactionChange, onOpenDetail }: Props) {
  const { people, viewer } = useViewer();
  const [busy, setBusy] = useState(false);

  const myReaction = viewer ? result.reactions[viewer] : null;
  const otherPeople = people.filter((p) => p.key !== viewer);

  const handleReact = async (reaction: ReactionValue) => {
    if (!viewer || busy) return;
    setBusy(true);
    const next = myReaction === reaction ? null : reaction;
    try {
      await setReaction(viewer, result.name_id, result.sex, next);
      onReactionChange(result.name_id, result.sex, viewer, next);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`name-card ${myReaction === "veto" ? "is-vetoed" : ""}`}>
      <button className="name-card__name" onClick={() => onOpenDetail(result.name_id, result.sex)}>
        {result.name}
        <span className={`name-card__sex-badge sex-${result.sex}`}>{result.sex}</span>
      </button>

      <div className="name-card__countries">
        {result.countries.map((c) => (
          <span key={c.country_code} className="name-card__country-stat">
            {c.country_code} #{c.best_rank ?? "?"}
            {c.trend && <span className="name-card__trend">{TREND_ICON[c.trend] ?? ""}</span>}
          </span>
        ))}
      </div>

      <div className="name-card__meta">
        {result.length} letters &middot; {result.syllable_count ?? "?"} syllables
      </div>

      <div className="name-card__actions">
        <button
          className={`name-card__react ${myReaction === "favorite" ? "is-active" : ""}`}
          disabled={busy}
          onClick={() => handleReact("favorite")}
        >
          Favorite
        </button>
        <button
          className={`name-card__react ${myReaction === "veto" ? "is-active" : ""}`}
          disabled={busy}
          onClick={() => handleReact("veto")}
        >
          Veto
        </button>
      </div>

      {otherPeople.length > 0 && (
        <div className="name-card__other-reactions">
          {otherPeople.map((p) => {
            const r = result.reactions[p.key];
            if (!r) return null;
            return (
              <span key={p.key} className={`name-card__other-badge is-${r}`}>
                {p.display_name}: {r === "favorite" ? "favorited" : "vetoed"}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
