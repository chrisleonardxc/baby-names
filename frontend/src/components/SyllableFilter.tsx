import { DualRangeSlider } from "./DualRangeSlider";

const MIN = 1;
const MAX = 7;

interface Props {
  valueMin: number | null;
  valueMax: number | null;
  onChange: (min: number | null, max: number | null) => void;
}

export function SyllableFilter({ valueMin, valueMax, onChange }: Props) {
  const isAny = valueMin == null && valueMax == null;
  const isExact = (n: number) => valueMin === n && valueMax === n;

  return (
    <div className="syllable-filter">
      <div className="filter-panel__chips">
        <button className={isAny ? "is-active" : ""} onClick={() => onChange(null, null)}>
          Any
        </button>
        {Array.from({ length: MAX - MIN + 1 }, (_, i) => MIN + i).map((n) => (
          <button key={n} className={isExact(n) ? "is-active" : ""} onClick={() => onChange(n, n)}>
            {n}
          </button>
        ))}
      </div>
      <DualRangeSlider
        min={MIN}
        max={MAX}
        valueMin={valueMin ?? MIN}
        valueMax={valueMax ?? MAX}
        onChange={onChange}
        labelMin="Minimum syllables"
        labelMax="Maximum syllables"
      />
    </div>
  );
}
