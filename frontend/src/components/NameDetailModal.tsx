import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getNameDetail } from "../api/client";
import type { NameDetail } from "../api/types";

interface Props {
  nameId: number;
  sex: "M" | "F";
  onClose: () => void;
}

const COLORS = ["#4f46e5", "#dc2626", "#059669", "#d97706", "#7c3aed", "#0891b2"];

export function NameDetailModal({ nameId, sex, onClose }: Props) {
  const [detail, setDetail] = useState<NameDetail | null>(null);

  useEffect(() => {
    getNameDetail(nameId, sex).then(setDetail);
  }, [nameId, sex]);

  if (!detail) return null;

  const countryCodes = Array.from(new Set(detail.timeseries.map((t) => t.country_code)));
  const years = Array.from(new Set(detail.timeseries.map((t) => t.year))).sort((a, b) => a - b);
  const chartData = years.map((year) => {
    const row: Record<string, number | string> = { year };
    for (const cc of countryCodes) {
      const point = detail.timeseries.find((t) => t.year === year && t.country_code === cc);
      if (point?.rank != null) row[cc] = point.rank;
    }
    return row;
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal__close" onClick={onClose}>
          &times;
        </button>
        <h2>
          {detail.name} <span className={`name-card__sex-badge sex-${detail.sex}`}>{detail.sex}</span>
        </h2>
        <p className="modal__subtitle">Rank over time (lower is more popular)</p>
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis reversed label={{ value: "Rank", angle: -90, position: "insideLeft" }} />
              <Tooltip />
              <Legend />
              {countryCodes.map((cc, i) => (
                <Line
                  key={cc}
                  type="monotone"
                  dataKey={cc}
                  stroke={COLORS[i % COLORS.length]}
                  connectNulls
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
