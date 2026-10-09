"use client";

/**
 * Small animation primitives.
 *
 * Deliberately restrained: motion is used to show that something is happening
 * and to preserve spatial context, never to decorate. All of it degrades to
 * the final state when `prefers-reduced-motion` is set.
 */

import { useEffect, useRef, useState } from "react";

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined" || !window.matchMedia) return;
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(query.matches);
    const listener = (e: MediaQueryListEvent) => setReduced(e.matches);
    query.addEventListener("change", listener);
    return () => query.removeEventListener("change", listener);
  }, []);
  return reduced;
}

/** Counts up to `value`, respecting reduced-motion. Used for headline figures. */
export function CountUp({
  value,
  decimals = 0,
  durationMs = 900,
  suffix = "",
  className = "",
}: {
  value: number;
  decimals?: number;
  durationMs?: number;
  suffix?: string;
  className?: string;
}) {
  const reduced = useReducedMotion();
  const [display, setDisplay] = useState(reduced ? value : 0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    if (reduced) {
      setDisplay(value);
      return;
    }
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      // easeOutCubic
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(value * eased);
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, [value, durationMs, reduced]);

  return (
    <span className={className}>
      {display.toFixed(decimals)}
      {suffix}
    </span>
  );
}

/** Animates a bar width once it is mounted. */
export function GrowBar({
  value,
  className = "",
  delayMs = 0,
  height = "h-2.5",
}: {
  value: number;
  className?: string;
  delayMs?: number;
  height?: string;
}) {
  const reduced = useReducedMotion();
  const [width, setWidth] = useState(reduced ? value * 100 : 0);

  useEffect(() => {
    if (reduced) {
      setWidth(value * 100);
      return;
    }
    const id = window.setTimeout(() => setWidth(value * 100), delayMs);
    return () => window.clearTimeout(id);
  }, [value, delayMs, reduced]);

  return (
    <span className={`${height} block overflow-hidden rounded-full bg-track`}>
      <span
        className={`block h-full rounded-full transition-[width] duration-700 ease-out ${className}`}
        style={{ width: `${width}%` }}
      />
    </span>
  );
}

/** Soft looping pulse, used on live/loading indicators. */
export function PulseDot({
  color = "var(--mint-500)",
  size = 6,
  className = "",
}: {
  color?: string;
  size?: number;
  className?: string;
}) {
  return (
    <span className={`relative inline-flex ${className}`} style={{ width: size, height: size }}>
      <span className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60" style={{ background: color }} />
      <span className="relative inline-flex rounded-full" style={{ width: size, height: size, background: color }} />
    </span>
  );
}

/**
 * ECG-style trace that draws itself left to right. Used as ambient motion in
 * the summary card; purely decorative and hidden from assistive tech.
 */
export function EcgTrace({
  width = 220,
  height = 46,
  color = "var(--blush-500)",
  className = "",
}: {
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}) {
  const reduced = useReducedMotion();
  const [progress, setProgress] = useState(reduced ? 1 : 0);

  useEffect(() => {
    if (reduced) return;
    let raf: number | null = null;
    const start = performance.now();
    const loop = (now: number) => {
      const cycle = 2600;
      const t = ((now - start) % cycle) / cycle;
      // sweep forward then hold
      setProgress(t < 0.75 ? t / 0.75 : 1);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => {
      if (raf !== null) cancelAnimationFrame(raf);
    };
  }, [reduced]);

  // idle → flatline → P wave → QRS → T wave
  const points = `0,${height / 2} 22,${height / 2} 30,${height / 2 - 5} 38,${height / 2} 52,${height / 2} 60,${height / 2 - 12} 68,${height / 2 + 16} 76,${height / 2 - 20} 84,${height / 2} 100,${height / 2} 112,${height / 2 - 7} 122,${height / 2} ${width},${height / 2}`;

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      width={width}
      height={height}
      className={className}
      aria-hidden="true"
      preserveAspectRatio="none"
    >
      <line x1={0} y1={height / 2} x2={width} y2={height / 2} stroke="var(--line)" strokeWidth={1} />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={width * 1.6}
        strokeDashoffset={width * 1.6 * (1 - progress)}
      />
    </svg>
  );
}

/** Segmented ring that sweeps to its value once, then rests. */
export function SweepRing({
  value,
  size = 132,
  stroke = 4.5,
  segments = 60,
  track = "var(--line-2)",
  color = "var(--mint-500)",
  trackWidth = 3,
  label,
  display,
}: {
  value: number;
  size?: number;
  stroke?: number;
  segments?: number;
  track?: string;
  color?: string;
  trackWidth?: number;
  label?: string;
  display?: string;
}) {
  const reduced = useReducedMotion();
  const [p, setP] = useState(reduced ? value : 0);

  useEffect(() => {
    if (reduced) {
      setP(value);
      return;
    }
    const id = window.setTimeout(() => setP(value), 80);
    return () => window.clearTimeout(id);
  }, [value, reduced]);

  const cx = size / 2;
  const cy = size / 2;
  const filled = Math.round(p * segments);

  return (
    <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} role="img" aria-label={label}>
      {Array.from({ length: segments }).map((_, i) => {
        const angle = (i / segments) * 2 * Math.PI - Math.PI / 2;
        const inner = cx - stroke;
        return (
          <line
            key={i}
            x1={cx + Math.cos(angle) * inner}
            y1={cy + Math.sin(angle) * inner}
            x2={cx + Math.cos(angle) * cx}
            y2={cy + Math.sin(angle) * cy}
            stroke={i < filled ? color : track}
            strokeWidth={i < filled ? stroke : trackWidth}
            strokeLinecap="round"
            style={{ transition: "stroke .18s ease" }}
          />
        );
      })}
      {display && (
        <text
          x={cx}
          y={cy + 2}
          textAnchor="middle"
          className="fill-ink"
          style={{ fontSize: size * 0.19, fontWeight: 600, letterSpacing: "-0.02em" }}
        >
          {display}
        </text>
      )}
      {label && (
        <text
          x={cx}
          y={cy + 19}
          textAnchor="middle"
          className="fill-ink-faint"
          style={{ fontSize: size * 0.072 }}
        >
          {label}
        </text>
      )}
    </svg>
  );
}

/** Breathing halo for the hero anatomy figure. */
export function Breathe({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const reduced = useReducedMotion();
  if (reduced) return <div className={className}>{children}</div>;
  return (
    <div className={`animate-[breathe_5s_ease-in-out_infinite] ${className}`}>{children}</div>
  );
}

/** Staggered entrance wrapper for lists of cards. */
export function Reveal({
  children,
  index = 0,
  className = "",
}: {
  children: React.ReactNode;
  index?: number;
  className?: string;
}) {
  return (
    <div
      className={`animate-fade-up ${className}`}
      style={{ animationDelay: `${Math.min(index, 8) * 55}ms` }}
    >
      {children}
    </div>
  );
}