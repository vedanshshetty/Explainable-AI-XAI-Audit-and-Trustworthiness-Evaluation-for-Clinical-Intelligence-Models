import type { ConfidenceLevel } from "./types";

export function cx(...parts: Array<string | false | null | undefined>): string {
  return parts.filter(Boolean).join(" ");
}

export function pct(value: number | null | undefined): number {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.min(1, Math.max(0, n));
}

export function formatPct(value: number | null | undefined): string {
  return `${Math.round(pct(value) * 100)}%`;
}

/** Tone classes for confidence bands. */
export function levelTone(level: ConfidenceLevel | string): {
  text: string;
  chip: string;
  bar: string;
  soft: string;
} {
  switch (String(level).toLowerCase()) {
    case "high":
      return {
        text: "text-mint-700",
        chip: "bg-mint-100 text-mint-700 border-mint-200",
        bar: "bg-mint-500",
        soft: "bg-mint-50 border-mint-200",
      };
    case "medium":
      return {
        text: "text-butter-700",
        chip: "bg-butter-100 text-butter-700 border-butter-200",
        bar: "bg-butter-500",
        soft: "bg-butter-50 border-butter-200",
      };
    case "low":
      return {
        text: "text-blush-700",
        chip: "bg-blush-100 text-blush-700 border-blush-200",
        bar: "bg-blush-500",
        soft: "bg-blush-50 border-blush-200",
      };
    default:
      return {
        text: "text-sky-700",
        chip: "bg-sky-100 text-sky-700 border-sky-200",
        bar: "bg-sky-500",
        soft: "bg-sky-50 border-sky-200",
      };
  }
}

export function severityTone(severity: string): { wrap: string; label: string; dot: string } {
  switch (String(severity).toLowerCase()) {
    case "critical":
      return {
        wrap: "bg-blush-50 border-blush-200",
        label: "text-blush-700",
        dot: "bg-blush-500",
      };
    case "warning":
      return {
        wrap: "bg-butter-50 border-butter-200",
        label: "text-butter-700",
        dot: "bg-butter-500",
      };
    default:
      return {
        wrap: "bg-sky-50 border-sky-200",
        label: "text-sky-700",
        dot: "bg-sky-500",
      };
  }
}

export function titleCase(value: string): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Stable pastel assignment so a source keeps the same colour across renders. */
const PALETTE = [
  { bg: "bg-lilac-100", text: "text-lilac-700" },
  { bg: "bg-mint-100", text: "text-mint-700" },
  { bg: "bg-sky-100", text: "text-sky-700" },
  { bg: "bg-butter-100", text: "text-butter-700" },
  { bg: "bg-blush-100", text: "text-blush-700" },
];

export function toneForIndex(index: number): { bg: string; text: string } {
  return PALETTE[((index - 1) % PALETTE.length + PALETTE.length) % PALETTE.length];
}

/** Strip [Source N] markers so a citation chip can be rendered inline instead. */
export function stripMarkers(text: string): string {
  return text.replace(/\[Source\s*#?\d+\]/gi, "").replace(/\s{2,}/g, " ").trim();
}

/** Extract the source numbers referenced by a piece of text. */
export function markersIn(text: string): number[] {
  const found: number[] = [];
  const matches = text.match(/\[Source\s*#?(\d+)\]/gi) || [];
  for (const m of matches) {
    const n = parseInt(m.replace(/\D/g, ""), 10);
    if (Number.isFinite(n) && !found.includes(n)) found.push(n);
  }
  return found;
}

export function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return `${text.slice(0, max - 1).trimEnd()}…`;
}