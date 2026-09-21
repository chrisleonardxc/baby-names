import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Local draft state for a two-thumb slider that only commits once the user pauses.
 * Dragging a thumb fires onChange for every step it crosses; committing each one
 * would send a (potentially expensive) search request per step. The draft updates
 * immediately so labels/thumbs stay live, and onCommit fires `delayMs` after the
 * last movement -- or right away on unmount, so a pending change is never lost
 * (e.g. when the filter panel is collapsed mid-drag). Pass `immediate` for
 * discrete actions like preset buttons.
 */
export function useDebouncedRange(
  valueMin: number,
  valueMax: number,
  onCommit: (min: number, max: number) => void,
  delayMs = 300,
): [number, number, (min: number, max: number, immediate?: boolean) => void] {
  const [draft, setDraft] = useState<[number, number]>([valueMin, valueMax]);
  const pending = useRef<[number, number] | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const commitRef = useRef(onCommit);

  useEffect(() => {
    commitRef.current = onCommit;
  });

  // Follow external changes (presets, back/forward navigation).
  useEffect(() => {
    setDraft([valueMin, valueMax]);
  }, [valueMin, valueMax]);

  const flush = useCallback(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    const next = pending.current;
    pending.current = null;
    if (next) commitRef.current(next[0], next[1]);
  }, []);

  useEffect(() => flush, [flush]);

  const update = useCallback(
    (min: number, max: number, immediate = false) => {
      setDraft([min, max]);
      pending.current = [min, max];
      if (timer.current) clearTimeout(timer.current);
      if (immediate) flush();
      else timer.current = setTimeout(flush, delayMs);
    },
    [delayMs, flush],
  );

  return [draft[0], draft[1], update];
}
