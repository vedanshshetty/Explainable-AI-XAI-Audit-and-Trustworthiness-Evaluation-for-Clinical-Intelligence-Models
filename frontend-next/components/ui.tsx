"use client";

import type { ReactNode } from "react";
import { cx } from "@/lib/utils";
import { CountUp, GrowBar } from "./Motion";

export function Card({
  title,
  subtitle,
  action,
  tone = "white",
  className = "",
  children,
}: {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  tone?: "white" | "lilac" | "mint" | "butter" | "sky" | "blush";
  className?: string;
  children: ReactNode;
}) {
  const tones: Record<string, string> = {
    white: "bg-surface border-line",
    lilac: "bg-lilac-50 border-lilac-200",
    mint: "bg-mint-50 border-mint-200",
    butter: "bg-butter-50 border-butter-200",
    sky: "bg-sky-50 border-sky-200",
    blush: "bg-blush-50 border-blush-200",
  };

  return (
    <section className={cx("rounded-2xl border shadow-card", tones[tone], className)}>
      {(title || action) && (
        <header className="flex items-start justify-between gap-3 px-5 pb-2 pt-4">
          <div className="min-w-0">
            {title && <h2 className="text-[14px] font-semibold tracking-tight text-ink">{title}</h2>}
            {subtitle && <p className="mt-0.5 text-[12px] text-ink-muted">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className="px-5 pb-5 pt-1">{children}</div>
    </section>
  );
}

export function SectionHeading({
  title,
  count,
  hint,
}: {
  title: string;
  count?: number;
  hint?: string;
}) {
  return (
    <div className="mb-3 flex items-baseline gap-3">
      <h2 className="text-[13px] font-semibold uppercase tracking-wider text-ink-muted">{title}</h2>
      {typeof count === "number" && (
        <span className="rounded-full bg-canvas px-2 py-0.5 text-[11px] font-medium text-ink-faint">
          {count}
        </span>
      )}
      {hint && <span className="text-[11.5px] text-ink-faint">{hint}</span>}
      <span className="h-px flex-1 bg-line" />
    </div>
  );
}

export function StatTile({
  label,
  value,
  detail,
  tone = "white",
  icon,
}: {
  label: string;
  value: string;
  detail?: string;
  tone?: "white" | "lilac" | "mint" | "butter" | "sky" | "blush";
  icon?: ReactNode;
}) {
  const tones: Record<string, string> = {
    white: "bg-surface border-line",
    lilac: "bg-lilac-100 border-lilac-200",
    mint: "bg-mint-100 border-mint-200",
    butter: "bg-butter-100 border-butter-200",
    sky: "bg-sky-100 border-sky-200",
    blush: "bg-blush-100 border-blush-200",
  };
  // Animate numeric tiles; leave labels like "3 docs" static.
  const grouped = value.includes(",");
  const numeric = parseFloat(value);
  const parseable = !grouped && Number.isFinite(numeric);
  // Only count digits after the decimal point; "1,024" must not read as 3 decimals.
  const decimals = parseable
    ? (value.split(".")[1]?.match(/^\d+/) ?.[0].length ?? 0)
    : 0;
  const suffix = parseable ? value.replace(/^[\d.,]+/, "") : "";

  return (
    <div className={cx("rounded-2xl border p-4 shadow-card transition-shadow duration-300 hover:shadow-lift", tones[tone])}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-[11.5px] font-medium text-ink-muted">{label}</p>
        {icon}
      </div>
      <p className="mt-2 text-[26px] font-semibold leading-none tracking-tight text-ink">
        {parseable ? (
          <CountUp value={numeric} decimals={decimals} suffix={suffix} />
        ) : (
          <span>{value}</span>
        )}
      </p>
      {detail && <p className="mt-1.5 text-[11.5px] text-ink-faint">{detail}</p>}
    </div>
  );
}

export function Meter({ value, tone }: { value: number; tone: string }) {
  return <GrowBar value={Math.min(100, Math.max(0, value * 100))} className={tone} height="h-1.5" />;
}

export function BarRow({ label, value, tone }: { label: string; value: number; tone: string }) {
  const width = Math.min(100, Math.max(0, value * 100));
  return (
    <div className="flex items-center gap-3 py-[3px]">
      <span className="w-[104px] shrink-0 truncate text-[12px] text-ink-muted" title={label}>
        {label}
      </span>
      <GrowBar value={width} className={tone} />
      <span className="w-11 shrink-0 text-right font-mono text-[11.5px] text-ink-soft">
        {Math.round(width)}%
      </span>
    </div>
  );
}

export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "mint" | "butter" | "blush" | "sky" | "lilac";
}) {
  const tones: Record<string, string> = {
    neutral: "bg-canvas text-ink-muted border-line",
    mint: "bg-mint-100 text-mint-700 border-mint-200",
    butter: "bg-butter-100 text-butter-700 border-butter-200",
    blush: "bg-blush-100 text-blush-700 border-blush-200",
    sky: "bg-sky-100 text-sky-700 border-sky-200",
    lilac: "bg-lilac-100 text-lilac-700 border-lilac-200",
  };
  return (
    <span className={cx("inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-semibold", tones[tone])}>
      {children}
    </span>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={cx(
        "animate-shimmer rounded-lg bg-[linear-gradient(90deg,rgba(15,23,42,0.045)_0%,rgba(15,23,42,0.085)_50%,rgba(15,23,42,0.045)_100%)] bg-[length:1000px_100%]",
        className,
      )}
    />
  );
}