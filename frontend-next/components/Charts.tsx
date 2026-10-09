"use client";

import { cx, formatPct, pct } from "@/lib/utils";
import { GrowBar, SweepRing } from "./Motion";
import type { SourceEvidence } from "@/lib/types";

/**
 * Relevance by source. Hand-rolled SVG so the whole surface keeps the soft
 * palette without pulling in a charting library.
 */
export function EvidenceChart({ evidence }: { evidence: SourceEvidence[] }) {
  if (evidence.length === 0) {
    return <p className="py-6 text-center text-[12.5px] text-ink-faint">No sources to chart.</p>;
  }

  const W = 640;
  const H = 190;
  const padL = 34;
  const padR = 10;
  const padT = 14;
  const padB = 28;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;

  const points = evidence.map((src) => {
    const normalized = src.relevance_normalized ?? 1 / (1 + Math.exp(-(src.relevance_score || 0)));
    return { src, value: pct(normalized) };
  });

  const scale = (Math.max(...points.map((p) => p.value)) || 0.5) * 1.2;
  const step = plotW / points.length;
  const barW = Math.min(46, step * 0.52);

  const ticks = [0, 0.5, 1].map((f) => ({
    y: padT + plotH - f * plotH,
    label: Math.round(f * scale * 100),
  }));

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Relevance of each retrieved source">
        {ticks.map((t) => (
          <g key={t.label}>
            <line x1={padL} y1={t.y} x2={W - padR} y2={t.y} stroke="var(--line)" strokeWidth={1} />
            <text x={padL - 8} y={t.y + 3.5} textAnchor="end" className="fill-ink-faint font-mono text-[9px]">
              {t.label}
            </text>
          </g>
        ))}

        {points.map(({ src, value }, i) => {
          const x = padL + step * (i + 0.5);
          const barH = scale > 0 ? (value / scale) * plotH : 0;
          const y = padT + plotH - barH;
          return (
            <g key={src.source_id}>
              <rect
                x={x - barW / 2}
                y={y}
                width={barW}
                height={Math.max(2, barH)}
                rx={6}
                className="fill-mint-500"
                opacity={src.cited ? 0.95 : 0.5}
              />
              {src.cited && (
                <circle cx={x} cy={Math.max(7, y - 8)} r={3.5} className="fill-butter-500" />
              )}
              <text
                x={x}
                y={H - 9}
                textAnchor="middle"
                className="fill-ink-faint font-mono text-[10px]"
              >
                S{src.citation_index}
              </text>
            </g>
          );
        })}
      </svg>

      <div className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-[11.5px] text-ink-muted">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-mint-500" /> Normalised relevance
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-butter-500" /> Cited in the answer
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-mint-500 opacity-50" /> Retrieved, not cited
        </span>
      </div>
    </div>
  );
}

/** Confidence per hypothesis as horizontal bars. */
export function ConfidenceChart({
  hypotheses,
}: {
  hypotheses: Array<{ condition: string; confidence: number; confidence_level: string }>;
}) {
  if (hypotheses.length === 0) {
    return <p className="py-6 text-center text-[12.5px] text-ink-faint">No hypotheses to chart.</p>;
  }

  const toneFor = (level: string) =>
    level === "high" ? "bg-mint-500" : level === "medium" ? "bg-butter-500" : "bg-blush-500";

  return (
    <div className="space-y-2.5">
      {hypotheses.map((h, i) => (
        <div key={h.condition} className="flex items-center gap-3">
          <span className="w-[150px] shrink-0 truncate text-[12.5px] text-ink-soft" title={h.condition}>
            {h.condition}
          </span>
          <GrowBar
            value={pct(h.confidence) * 100}
            className={toneFor(h.confidence_level)}
            delayMs={i * 80}
          />
          <span className="w-11 shrink-0 text-right font-mono text-[12px] text-ink-soft">
            {Math.round(pct(h.confidence) * 100)}%
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Radial gauge used for the overall trust score.
 * `segments` renders the segmented ring from the reference dashboard.
 */
export function RadialGauge({
  value,
  label,
  segments = 60,
}: {
  value: number;
  label: string;
  segments?: number;
}) {
  return (
    <div className="flex flex-col items-center">
      <SweepRing
        value={pct(value)}
        size={140}
        segments={segments}
        display={formatPct(value)}
        label={label}
        color={pct(value) >= 0.7 ? "var(--mint-500)" : pct(value) >= 0.45 ? "var(--butter-500)" : "var(--blush-500)"}
      />
    </div>
  );
}

/** Compact sparkline for a short numeric series. */
export function Sparkline({
  values,
  stroke = "var(--lilac-500)",
  width = 120,
  height = 34,
}: {
  values: number[];
  stroke?: string;
  width?: number;
  height?: number;
}) {
  if (values.length < 2) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const span = max - min || 1;
  const step = width / (values.length - 1);
  const coords = values.map((v, i) => ({
    x: i * step,
    y: height - 3 - ((v - min) / span) * (height - 6),
  }));

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width={width} height={height} role="presentation">
      <polyline
        points={coords.map((c) => `${c.x.toFixed(1)},${c.y.toFixed(1)}`).join(" ")}
        fill="none"
        stroke={stroke}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {coords.map((c, i) => (
        <circle key={i} cx={c.x} cy={c.y} r={2.2} fill={stroke} />
      ))}
    </svg>
  );
}