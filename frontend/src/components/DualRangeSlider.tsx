interface Tick {
  value: number;
  label: string;
}

interface Props {
  min: number;
  max: number;
  valueMin: number;
  valueMax: number;
  onChange: (min: number, max: number) => void;
  ticks?: Tick[];
  labelMin?: string;
  labelMax?: string;
}

/** A single track with two overlapping thumbs, sharing one visual bar/fill. */
export function DualRangeSlider({ min, max, valueMin, valueMax, onChange, ticks, labelMin, labelMax }: Props) {
  const span = max - min || 1;
  const pct = (value: number) => ((value - min) / span) * 100;

  const setRange = (a: number, b: number) => onChange(Math.min(a, b), Math.max(a, b));

  return (
    <div className="dual-range-slider">
      <div className="dual-range-slider__track">
        <div className="dual-range-slider__rail" />
        <div
          className="dual-range-slider__fill"
          style={{ left: `${pct(valueMin)}%`, width: `${pct(valueMax) - pct(valueMin)}%` }}
        />
        {ticks?.map((t, i) => (
          <div
            key={t.value}
            className={`dual-range-slider__tick ${i % 2 === 1 ? "dual-range-slider__tick--stagger" : ""}`}
            style={{ left: `${pct(t.value)}%` }}
          >
            <span>{t.label}</span>
          </div>
        ))}
        <input
          type="range"
          min={min}
          max={max}
          value={valueMin}
          onChange={(e) => setRange(Number(e.target.value), valueMax)}
          className="dual-range-slider__input"
          aria-label={labelMin ?? "Minimum"}
        />
        <input
          type="range"
          min={min}
          max={max}
          value={valueMax}
          onChange={(e) => setRange(valueMin, Number(e.target.value))}
          className="dual-range-slider__input"
          aria-label={labelMax ?? "Maximum"}
        />
      </div>
    </div>
  );
}
