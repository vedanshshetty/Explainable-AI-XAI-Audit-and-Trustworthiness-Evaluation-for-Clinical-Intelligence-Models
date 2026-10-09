"use client";

import { cx } from "@/lib/utils";
import { PulseDot } from "./Motion";
import { ThemeToggle } from "./ThemeToggle";

export type BackendState = "checking" | "ready" | "offline";

export function Topbar({
  state,
  model,
  corpus,
  onSearch,
}: {
  state: BackendState;
  model?: string;
  corpus?: number;
  onSearch: (value: string) => void;
}) {
  return (
    <header className="flex h-[68px] shrink-0 items-center gap-4 border-b border-line bg-surface px-6">
      {/* search */}
      <div className="relative w-full max-w-[380px]">
        <svg
          viewBox="0 0 20 20"
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <circle cx="9" cy="9" r="5.5" />
          <path d="M13.5 13.5L17 17" strokeLinecap="round" />
        </svg>
        <input
          type="search"
          placeholder="Search literature, conditions, PMIDs…"
          onChange={(e) => onSearch(e.target.value)}
          className="h-10 w-full rounded-full border border-line bg-canvas pl-9 pr-4 text-[13px] text-ink placeholder:text-ink-faint focus:border-lilac-200 focus:bg-surface focus:outline-none focus:ring-2 focus:ring-lilac-100"
        />
      </div>

      <div className="ml-auto flex items-center gap-3">
        {/* research disclaimer */}
        <span className="hidden rounded-full border border-butter-200 bg-butter-50 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-butter-700 sm:inline">
          Research only · not a medical device
        </span>

        {/* backend status */}
        <span
          className={cx(
            "inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-[11.5px] font-medium",
            state === "ready" && "border-mint-200 bg-mint-50 text-mint-700",
            state === "checking" && "border-line bg-canvas text-ink-muted",
            state === "offline" && "border-blush-200 bg-blush-50 text-blush-700",
          )}
        >
          {state === "checking" ? (
            <PulseDot color="var(--ink-faint)" />
          ) : (
            <PulseDot color={state === "ready" ? "var(--mint-500)" : "var(--blush-500)"} />
          )}
          {state === "ready" ? "Pipeline ready" : state === "checking" ? "Checking…" : "Backend offline"}
        </span>

        {/* theme switch */}
        <ThemeToggle />

        {/* profile */}
        <div className="flex items-center gap-2.5 rounded-full border border-line py-1 pl-1 pr-3.5">
          <span className="grid h-8 w-8 place-items-center rounded-full bg-lilac-100 text-[11px] font-semibold text-lilac-700">
            CI
          </span>
          <span className="hidden leading-tight md:block">
            <span className="block text-[12.5px] font-semibold text-ink">Research Console</span>
            <span className="block text-[11px] text-ink-faint">
              {state === "ready" && model ? model.split("/").pop() : "Local session"}
            </span>
          </span>
        </div>
      </div>
    </header>
  );
}

export function StatusStrip({
  state,
  corpus,
  indexed,
  inSync,
}: {
  state: BackendState;
  corpus?: number;
  indexed?: number;
  inSync?: boolean;
}) {
  if (state !== "ready") return null;
  return (
    <div className="flex flex-wrap items-center gap-x-5 gap-y-1 rounded-2xl border border-line bg-surface px-4 py-2.5 text-[11.5px] text-ink-muted shadow-card">
      <span>
        Corpus <strong className="font-semibold text-ink-soft">{corpus ?? 0}</strong> documents
      </span>
      <span className="text-line">|</span>
      <span>
        Indexed <strong className="font-semibold text-ink-soft">{indexed ?? 0}</strong>
      </span>
      <span className="text-line">|</span>
      <span className={inSync === false ? "font-medium text-blush-700" : "text-ink-muted"}>
        {inSync === false
          ? "Indexes out of sync — run scripts/build_index.py"
          : "Indexes in sync"}
      </span>
    </div>
  );
}