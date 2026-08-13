import { DualRangeSlider } from "./DualRangeSlider";

const RESOLUTION = 1000;
// >1 skews slider travel toward recent years (higher = more emphasis). At 3, the
// most recent ~20 years occupy roughly half the track even when the full range
// spans a century or more.
const CURVE = 3;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function indexForYear(year: number, minYear: number, maxYear: number): number {
  const span = maxYear - minYear;
  if (span <= 0) return RESOLUTION;
  const yearsAgo = clamp(maxYear - year, 0, span);
  const t = Math.pow(yearsAgo / span, 1 / CURVE);
  return Math.round((1 - t) * RESOLUTION);
}

function yearForIndex(index: number, minYear: number, maxYear: number): number {
  const span = maxYear - minYear;
  const t = 1 - clamp(index, 0, RESOLUTION) / RESOLUTION;
  const yearsAgo = span * Math.pow(t, CURVE);
  return Math.round(maxYear - yearsAgo);
}

interface Props {
  minYear: number;
  maxYear: number;
  valueMin: number;
  valueMax: number;
  onChange: (min: number, max: number) => void;
}

export function YearRangeSlider({ minYear, maxYear, valueMin, valueMax, onChange }: Props) {
  const indexMin = indexForYear(valueMin, minYear, maxYear);
  const indexMax = indexForYear(valueMax, minYear, maxYear);

  const setRange = (min: number, max: number) => {
    onChange(Math.min(min, max), Math.max(min, max));
  };

  const presets: { label: string; years: number | null }[] = [
    { label: "Last 10 yrs", years: 10 },
    { label: "Last 20 yrs", years: 20 },
    { label: "All time", years: null },
  ];

  const isPresetActive = (years: number | null) => {
    const expectedMin = years == null ? minYear : Math.max(minYear, maxYear - years + 1);
    return valueMin === expectedMin && valueMax === maxYear;
  };

  const span = maxYear - minYear;
  const ticks = [20, 10]
    .filter((yearsAgo) => yearsAgo < span)
    .map((yearsAgo) => ({
      value: indexForYear(maxYear - yearsAgo, minYear, maxYear),
      label: `-${yearsAgo}y`,
    }));

  return (
    <div className="year-range-slider">
      <div className="year-range-slider__presets">
        {presets.map((p) => (
          <button
            key={p.label}
            className={isPresetActive(p.years) ? "is-active" : ""}
            onClick={() =>
              setRange(p.years == null ? minYear : Math.max(minYear, maxYear - p.years + 1), maxYear)
            }
          >
            {p.label}
          </button>
        ))}
      </div>

      <DualRangeSlider
        min={0}
        max={RESOLUTION}
        valueMin={indexMin}
        valueMax={indexMax}
        onChange={(a, b) => setRange(yearForIndex(a, minYear, maxYear), yearForIndex(b, minYear, maxYear))}
        ticks={ticks}
        labelMin="Earliest year"
        labelMax="Latest year"
      />

      <div className="year-range-slider__labels">
        <span>{valueMin}</span>
        <span>{valueMax}</span>
      </div>
    </div>
  );
}
