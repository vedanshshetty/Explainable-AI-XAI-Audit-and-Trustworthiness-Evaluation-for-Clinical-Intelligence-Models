"use client";

import type { ReactElement } from "react";
import { cx, toneForIndex } from "@/lib/utils";
import { SAMPLE_CASES } from "@/lib/types";

/**
 * Sidebar navigation and one-click sample cases.
 */
export function Sidebar({
  view,
  onViewChange,
  onRunSample,
  activeCaseId,
}: {
  view: string;
  onViewChange: (v: "analysis" | "cases" | "xai" | "trust") => void;
  onRunSample: (id: string, text: string) => void;
  activeCaseId: string | null;
}) {
  const nav: Array<{ key: "analysis" | "cases" | "xai" | "trust"; label: string; icon: ReactElement }> = [
    {
      key: "analysis",
      label: "Analysis",
      icon: (
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
          <rect x="2.5" y="2.5" width="6.5" height="6.5" rx="1.6" />
          <rect x="11" y="2.5" width="6.5" height="6.5" rx="1.6" />
          <rect x="2.5" y="11" width="6.5" height="6.5" rx="1.6" />
          <rect x="11" y="11" width="6.5" height="6.5" rx="1.6" />
        </svg>
      ),
    },
    {
      key: "cases",
      label: "Sample Cases",
      icon: (
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
          <path d="M10 10.5a3 3 0 100-6 3 3 0 000 6z" />
          <path d="M3.5 17c.6-3.2 3.3-5 6.5-5s5.9 1.8 6.5 5" strokeLinecap="round" />
        </svg>
      ),
    },
    {
      key: "xai",
      label: "Explainable AI",
      icon: (
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
          <circle cx="10" cy="10" r="3" />
          <path d="M10 2v2.2M10 15.8V18M18 10h-2.2M4.2 10H2M15.7 4.3l-1.5 1.5M5.8 14.2l-1.5 1.5M15.7 15.7l-1.5-1.5M5.8 5.8L4.3 4.3" strokeLinecap="round" />
        </svg>
      ),
    },
    {
      key: "trust",
      label: "Trust Evaluation",
      icon: (
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
          <path d="M10 2.5l6 2.2v4.6c0 3.6-2.5 6.6-6 8.2-3.5-1.6-6-4.6-6-8.2V4.7l6-2.2z" strokeLinejoin="round" />
          <path d="M7.4 9.9l1.9 1.9 3.4-3.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ),
    },
  ];

  return (
    <aside className="flex w-[248px] shrink-0 flex-col border-r border-line bg-surface">
      {/* brand */}
      <div className="flex items-center gap-2.5 px-5 py-5">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-lilac-100 text-lilac-700">
          <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 12h3.2l2-5.4 3.4 11L15.6 12H21" />
          </svg>
        </span>
        <div className="leading-tight">
          <p className="text-[15px] font-semibold tracking-tight text-ink">
            Clinical<span className="text-lilac-700">Intel</span>
          </p>
          <p className="text-[11px] text-ink-faint">Research Console</p>
        </div>
      </div>

      <nav className="px-3">
        <p className="px-3 pb-2 pt-3 text-[11px] font-medium uppercase tracking-wider text-ink-faint">
          Main Menu
        </p>
        <ul className="space-y-0.5">
          {nav.map((item) => {
            const active = view === item.key;
            return (
              <li key={item.key}>
                <button
                  type="button"
                  onClick={() => onViewChange(item.key)}
                  className={cx(
                    "flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-[13.5px] font-medium transition-colors",
                    active
                      ? "bg-lilac-100 text-lilac-700"
                      : "text-ink-soft hover:bg-canvas hover:text-ink",
                  )}
                >
                  <span className={cx(active ? "text-lilac-700" : "text-ink-faint")}>{item.icon}</span>
                  {item.label}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* sample cases */}
      <div className="mt-5 min-h-0 flex-1 overflow-y-auto px-3 pb-4">
        <p className="px-3 pb-2 pt-3 text-[11px] font-medium uppercase tracking-wider text-ink-faint">
          Quick Cases
        </p>
        <CaseList onRun={onRunSample} activeCaseId={activeCaseId} />
      </div>

      <div className="border-t border-line px-5 py-4">
        <p className="text-[11px] leading-relaxed text-ink-faint">
          Research prototype. Not a medical device.
        </p>
      </div>
    </aside>
  );
}

function CaseList({
  onRun,
  activeCaseId,
}: {
  onRun: (id: string, text: string) => void;
  activeCaseId: string | null;
}) {
  return (
    <ul className="space-y-1.5">
      {SAMPLE_CASES.map((sample, i) => {
        const tone = toneForIndex(i + 1);
        const active = activeCaseId === sample.id;
        return (
          <li key={sample.id}>
            <button
              type="button"
              onClick={() => onRun(sample.id, sample.text)}
              className={cx(
                "w-full rounded-xl border px-3 py-2.5 text-left transition-all",
                active
                  ? "border-lilac-200 bg-lilac-50 shadow-card"
                  : "border-line bg-surface hover:border-lilac-200 hover:bg-lilac-50",
              )}
            >
              <div className="flex items-start gap-2.5">
                <span className={cx("mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg text-[11px] font-semibold", tone.bg, tone.text)}>
                  {sample.label
                    .split(" ")
                    .slice(0, 2)
                    .map((w) => w[0])
                    .join("")
                    .toUpperCase()}
                </span>
                <span className="min-w-0">
                  <span className="block truncate text-[12.5px] font-medium text-ink">{sample.label}</span>
                  <span className="block truncate text-[11px] text-ink-faint">{sample.focus}</span>
                </span>
              </div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}