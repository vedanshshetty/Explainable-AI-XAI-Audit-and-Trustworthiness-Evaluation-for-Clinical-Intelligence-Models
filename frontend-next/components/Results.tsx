"use client";

import { useState } from "react";
import {
  Badge,
  BarRow,
  Card,
  Meter,
  SectionHeading,
  StatTile,
} from "./ui";
import { ConfidenceChart, EvidenceChart, RadialGauge, Sparkline } from "./Charts";
import { Breathe, CountUp, EcgTrace, GrowBar, PulseDot, Reveal, SweepRing } from "./Motion";
import { AnatomyFigure, figureForText } from "./Anatomy";
import {
  cx,
  formatPct,
  levelTone,
  markersIn,
  pct,
  severityTone,
  stripMarkers,
  titleCase,
  toneForIndex,
  truncate,
} from "@/lib/utils";
import type { AnalysisResponse } from "@/lib/types";

/* ── A. Summary ─────────────────────────────────────────────────────────── */

/** Pull the vital signs actually stated in the case text. Nothing is invented. */
export function extractVitals(text: string): Array<{ label: string; value: string; unit?: string }> {
  const found: Array<{ label: string; value: string; unit?: string }> = [];
  const t = text;
  const push = (label: string, re: RegExp, unit?: string) => {
    const m = t.match(re);
    if (m) found.push({ label, value: m[1], unit });
  };
  push("Temperature", /(\d{2}(?:\.\d)?)\s*(?:C|°C|degrees C)/i, "°C");
  push("Heart rate", /(?:HR|heart rate|pulse)[^0-9]{0,12}(\d{2,3})/i, "bpm");
  push("Respiratory rate", /(?:RR|respiratory rate)[^0-9]{0,12}(\d{1,2})\b/i, "/min");
  push("Systolic BP", /(?:BP|blood pressure)[^0-9]{0,12}(\d{2,3})\s*\/\s*\d{2,3}/i, "mmHg");
  push("Oxygen sat", /SpO2[^0-9]{0,10}(\d{2})\s*%/i, "%");
  return found.slice(0, 6);
}

/** Animated vitals strip. Values come only from the case text. */
function VitalsStrip({ text }: { text: string }) {
  const vitals = extractVitals(text);
  if (vitals.length === 0) return null;
  return (
    <div className="mt-4 border-t border-line pt-3">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-ink-faint">
        Vitals stated in the case
      </p>
      <div className="flex flex-wrap gap-2">
        {vitals.map((v, i) => (
          <div
            key={v.label}
            className="animate-scale-in flex items-baseline gap-1.5 rounded-xl border border-line bg-surface px-3 py-1.5 shadow-pill"
            style={{ animationDelay: `${i * 70}ms` }}
          >
            <span className="text-[10.5px] uppercase tracking-wide text-ink-faint">{v.label}</span>
            <span className="font-mono text-[13px] font-semibold text-ink">{v.value}</span>
            {v.unit && <span className="text-[10.5px] text-ink-faint">{v.unit}</span>}
          </div>
        ))}
      </div>
      <EcgTrace width={260} height={38} className="mt-2.5 w-full max-w-[260px] opacity-80" />
    </div>
  );
}

export function SummaryPanel({
  result,
  caseText,
  elapsed,
}: {
  result: AnalysisResponse;
  caseText: string;
  elapsed: number;
}) {
  const level = result.confidence_level;
  const tone = levelTone(level);
  const figure = figureForText(caseText);
  const refCounts = new Map<number, number>();
  for (const hyp of result.condition_hypotheses) {
    for (const n of markersIn(hyp.condition) || hyp.source_refs) {
      refCounts.set(n, (refCounts.get(n) ?? 0) + 1);
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile
          label="Confidence"
          value={formatPct(result.confidence_overall)}
          detail={`${titleCase(level)} confidence`}
          tone={level === "high" ? "mint" : level === "medium" ? "butter" : "blush"}
        />
        <StatTile
          label="Hypotheses"
          value={String(result.condition_hypotheses.length)}
          detail="conditions considered"
          tone="lilac"
        />
        <StatTile
          label="Sources"
          value={String(result.evidence.length)}
          detail={`${result.retrieval_count} retrieved`}
          tone="sky"
        />
        <StatTile
          label="Citation validity"
          value={formatPct(result.citation_validity)}
          detail={`${result.citations_used} markers emitted`}
          tone={pct(result.citation_validity) >= 0.8 ? "mint" : "butter"}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        {/* Clinical impression + figure */}
        <Card title="Clinical summary" subtitle="Generated from the retrieved literature">
          <div className="flex gap-4">
            <div className="min-w-0 flex-1">
              <p className="text-[13.5px] leading-[1.75] text-ink-soft">{result.summary}</p>

              <div className="mt-4 flex flex-wrap items-center gap-2">
                <span className={cx("rounded-full px-2.5 py-1 text-[11.5px] font-semibold", tone.chip)}>
                  {formatPct(result.confidence_overall)} · {level}
                </span>
                <span className="rounded-full bg-canvas px-2.5 py-1 text-[11.5px] text-ink-muted">
                  {titleCase(figure)} focus
                </span>
                <span className="rounded-full bg-canvas px-2.5 py-1 font-mono text-[11px] text-ink-faint">
                  case {result.case_id.slice(0, 8)}
                </span>
              </div>

              <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 border-t border-line pt-3 text-[12px] sm:grid-cols-4">
                <Meta label="Model" value={result.model_used?.split("/").pop() ?? "—"} />
                <Meta label="Provider" value={result.provider ?? "—"} />
                <Meta label="API time" value={`${result.processing_time_ms} ms`} />
                <Meta label="Round trip" value={`${elapsed} ms`} />
              </dl>

              <VitalsStrip text={caseText} />
            </div>

            <div className="hidden shrink-0 overflow-hidden sm:block sm:w-[176px]">
              <div className="relative flex h-[200px] w-full items-center justify-center">
                <span className="animate-halo pointer-events-none absolute inset-3 rounded-full bg-lilac-200 opacity-70 blur-2xl" />
                <Breathe className="relative flex h-full w-full items-center justify-center">
                  <AnatomyFigure kind={figure} className="h-full max-h-full w-auto max-w-full" />
                </Breathe>
              </div>
            </div>
          </div>
        </Card>

        {/* Confidence by hypothesis */}
        <Card
          title="Confidence by hypothesis"
          subtitle="Colour indicates the confidence band"
          tone="lilac"
        >
          <ConfidenceChart hypotheses={result.condition_hypotheses} />
          <p className="mt-3 border-t border-lilac-200 pt-2.5 text-[11.5px] text-ink-muted">
            {result.condition_hypotheses.length > 0
              ? `${titleCase(result.condition_hypotheses[0].condition)} leads at ${formatPct(
                  result.condition_hypotheses[0].confidence,
                )}.`
              : "No hypotheses were returned."}
          </p>
        </Card>
      </div>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] uppercase tracking-wide text-ink-faint">{label}</dt>
      <dd className="mt-0.5 truncate font-medium text-ink-soft">{value}</dd>
    </div>
  );
}

/* ── B. Safety flags ────────────────────────────────────────────────────── */

export function SafetyPanel({ result }: { result: AnalysisResponse }) {
  const flags = result.safety_flags;
  if (!flags || flags.length === 0) {
    return (
      <Card title="Safety flags" tone="mint">
        <p className="flex items-center gap-2 text-[13px] text-mint-700">
          <span className="grid h-5 w-5 place-items-center rounded-full bg-mint-100 text-[11px]">✓</span>
          No safety flags were raised for this case.
        </p>
      </Card>
    );
  }

  const critical = flags.filter((f) => f.severity === "critical");
  const rest = flags.filter((f) => f.severity !== "critical");

  return (
    <div className="space-y-3">
      {critical.map((flag, i) => {
        const t = severityTone(flag.severity);
        return (
          <div key={`c${i}`} className="rounded-2xl border border-blush-200 bg-blush-50 p-4 shadow-card">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-blush-500 text-on-solid">
                <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10 6v5M10 14h.01" strokeLinecap="round" />
                  <circle cx="10" cy="10" r="7.2" />
                </svg>
              </span>
              <div className="min-w-0">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-blush-700">
                  Critical · {titleCase(flag.flag_type)}
                </p>
                <p className="mt-1 text-[14px] font-semibold text-ink">{flag.message}</p>
                <p className="mt-1.5 text-[12.5px] leading-relaxed text-ink-muted">
                  Escalate to a qualified clinician before any further workup. This tool does not
                  provide definitive diagnoses.
                </p>
              </div>
            </div>
          </div>
        );
      })}

      {rest.length > 0 && (
        <div className="grid gap-2.5 md:grid-cols-2">
          {rest.map((flag, i) => {
            const t = severityTone(flag.severity);
            return (
              <div key={`w${i}`} className={cx("rounded-xl border p-3.5 shadow-card", t.wrap)}>
                <p className={cx("text-[11px] font-semibold uppercase tracking-wider", t.label)}>
                  {titleCase(flag.severity)} · {titleCase(flag.flag_type)}
                </p>
                <p className="mt-1 text-[13px] leading-relaxed text-ink-soft">{flag.message}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ── C. Hypotheses ──────────────────────────────────────────────────────── */

export function HypothesisPanel({ result }: { result: AnalysisResponse }) {
  const hyps = result.condition_hypotheses;
  if (hyps.length === 0) {
    return (
      <Card title="Condition hypotheses">
        <p className="text-[13px] text-ink-muted">
          Insufficient information to generate reliable hypotheses.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {hyps.map((hyp, i) => {
        const tone = levelTone(hyp.confidence_level);
        return (
          <Reveal
            key={`${hyp.condition}-${i}`}
            index={i}
            className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lift"
          >
            <div className={cx("h-1 w-full", tone.bar)} />
            <div className="p-4">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-canvas text-[11px] font-semibold text-ink-muted">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className="text-[15px] font-semibold tracking-tight text-ink">{hyp.condition}</h3>
                {hyp.icd10_code && (
                  <span className="rounded-full bg-canvas px-2 py-0.5 font-mono text-[11px] text-ink-faint">
                    {hyp.icd10_code}
                  </span>
                )}
                <span className="ml-auto flex items-center gap-2">
                  <span className={cx("text-[15px] font-semibold", tone.text)}>
                    {formatPct(hyp.confidence)}
                  </span>
                  <span className={cx("rounded-full border px-2.5 py-1 text-[11px] font-semibold", tone.chip)}>
                    {hyp.confidence_level}
                  </span>
                </span>
              </div>

              <div className="mt-3">
                <Meter value={hyp.confidence} tone={tone.bar} />
              </div>

              {hyp.source_refs.length > 0 && (
                <div className="mt-3 flex flex-wrap items-center gap-1.5">
                  <span className="text-[11px] text-ink-faint">Evidence:</span>
                  {hyp.source_refs.map((n) => {
                    const idx = toneForIndex(n);
                    return (
                      <span
                        key={n}
                        className={cx(
                          "rounded-md px-1.5 py-0.5 font-mono text-[10.5px] font-medium",
                          idx.bg,
                          idx.text,
                        )}
                      >
                        S{n}
                      </span>
                    );
                  })}
                </div>
              )}

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {hyp.supporting_factors.length > 0 && (
                  <FactorList title="Supporting" tone="mint" items={hyp.supporting_factors} />
                )}
                {hyp.against_factors.length > 0 && (
                  <FactorList title="Against" tone="blush" items={hyp.against_factors} />
                )}
              </div>

              {hyp.recommended_workup.length > 0 && (
                <div className="mt-3.5">
                  <FactorList title="Suggested workup" tone="sky" items={hyp.recommended_workup} inline />
                </div>
              )}
            </div>
          </Reveal>
        );
      })}
    </div>
  );
}

function FactorList({
  title,
  tone,
  items,
  inline = false,
}: {
  title: string;
  tone: "mint" | "blush" | "sky";
  items: string[];
  inline?: boolean;
}) {
  const dot: Record<string, string> = {
    mint: "bg-mint-500",
    blush: "bg-blush-500",
    sky: "bg-sky-500",
  };
  const label: Record<string, string> = {
    mint: "text-mint-700",
    blush: "text-blush-700",
    sky: "text-sky-700",
  };

  return (
    <div>
      <p className={cx("mb-1.5 text-[11px] font-semibold uppercase tracking-wider", label[tone])}>
        {title}
      </p>
      <ul className={cx(inline ? "flex flex-wrap gap-x-5 gap-y-1" : "space-y-1")}>
        {items.map((item, i) => {
          const refs = markersIn(item);
          const text = stripMarkers(item);
          return (
            <li key={i} className={cx("flex gap-2 text-[12.5px] leading-relaxed text-ink-soft", !inline && "") }>
              <span className={cx("mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full", dot[tone])} />
              <span>
                {text || "—"}
                {refs.length > 0 && (
                  <span className="ml-1.5 inline-flex gap-1 align-middle">
                    {refs.map((n) => (
                      <span
                        key={n}
                        className={cx(
                          "rounded px-1 py-px font-mono text-[10px]",
                          toneForIndex(n).bg,
                          toneForIndex(n).text,
                        )}
                      >
                        S{n}
                      </span>
                    ))}
                  </span>
                )}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/* ── D. Differential reasoning ───────────────────────────────────────────── */

export function ReasoningPanel({ result }: { result: AnalysisResponse }) {
  if (!result.differential_reasoning) return null;
  return (
    <Card title="Differential reasoning" subtitle="How the candidates were discriminated">
      <p className="text-[13.5px] leading-[1.78] text-ink-soft">{result.differential_reasoning}</p>
    </Card>
  );
}

/* ── E. Sources & citations ─────────────────────────────────────────────── */

export function SourcesPanel({ result }: { result: AnalysisResponse }) {
  const evidence = result.evidence;
  if (evidence.length === 0) {
    return (
      <Card title="Sources & citations">
        <p className="text-[13px] text-ink-muted">No sources were retrieved for this case.</p>
      </Card>
    );
  }

  const attributionSeries = evidence.map((e) => e.attribution_score);

  return (
    <div className="space-y-3">
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <Card
          title="Evidence relevance"
          subtitle={`${result.citations_used} markers · ${formatPct(result.citation_validity)} valid · ${formatPct(
            result.citation_coverage,
          )} coverage`}
          tone="mint"
        >
          <EvidenceChart evidence={evidence} />
        </Card>

        <Card title="Attribution spread" subtitle="Share of the answer carried by each source" tone="lilac">
          <div className="space-y-1">
            {evidence.map((e) => (
              <BarRow
                key={e.source_id}
                label={`S${e.citation_index} ${truncate(e.title, 22)}`}
                value={e.attribution_score}
                tone={e.cited ? "bg-lilac-500" : "bg-lilac-200"}
              />
            ))}
          </div>
          <div className="mt-3 flex items-center justify-between border-t border-lilac-200 pt-2.5">
            <span className="text-[11.5px] text-ink-muted">Attribution trend</span>
            <Sparkline values={attributionSeries} />
          </div>
        </Card>
      </div>

      <SectionHeading title="Citation detail" count={evidence.length} />
      <div className="grid gap-2.5 md:grid-cols-2">
        {evidence.map((src) => (
          <SourceCard key={src.source_id} source={src} />
        ))}
      </div>
    </div>
  );
}

function SourceCard({ source }: { source: AnalysisResponse["evidence"][number] }) {
  const [open, setOpen] = useState(false);
  const venue = source.year ? `${source.journal} · ${source.year}` : source.journal || "Journal not recorded";

  return (
    <article className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-start gap-3 p-4 text-left transition-colors hover:bg-canvas"
      >
        <span
          className={cx(
            "grid h-8 w-8 shrink-0 place-items-center rounded-lg text-[12px] font-semibold",
            source.cited ? "bg-mint-500 text-on-solid" : "bg-canvas text-ink-muted",
          )}
        >
          S{source.citation_index}
        </span>

        <span className="min-w-0 flex-1">
          <span className="block text-[13.5px] font-semibold leading-snug text-ink">{source.title}</span>
          <span className="mt-1 block text-[11.5px] text-ink-muted">{venue}</span>
          <span className="mt-1.5 flex flex-wrap items-center gap-2">
            {source.pmid_url ? (
              <a
                href={source.pmid_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 rounded-full bg-sky-50 px-2 py-0.5 text-[11px] font-medium text-sky-700 hover:bg-sky-100"
              >
                PMID {source.pmid}
                <svg viewBox="0 0 12 12" className="h-2.5 w-2.5" fill="none" stroke="currentColor" strokeWidth="1.6">
                  <path d="M4 2h6v6M10 2L2.5 9.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </a>
            ) : (
              source.pmid && (
                <span className="rounded-full bg-canvas px-2 py-0.5 font-mono text-[10.5px] text-ink-faint">
                  PMID {source.pmid} · local corpus
                </span>
              )
            )}
            <span
              className={cx(
                "rounded-full border px-2 py-0.5 text-[10.5px] font-semibold",
                source.cited ? "border-mint-200 bg-mint-50 text-mint-700" : "border-line bg-canvas text-ink-faint",
              )}
            >
              {source.cited ? "Cited" : "Retrieved, unused"}
            </span>
          </span>
        </span>

        <svg
          viewBox="0 0 20 20"
          className={cx("mt-1 h-4 w-4 shrink-0 text-ink-faint transition-transform", open && "rotate-180")}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        >
          <path d="M5 8l5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {open && (
        <div className="animate-fade-up border-t border-line bg-canvas px-4 pb-4 pt-3.5 animate-[slide-in_.24s_ease-out]">
          <div className="grid gap-2 sm:grid-cols-2">
            <ScoreLine label="Relevance" value={formatPct(source.relevance_normalized)} tone="bg-mint-500" />
            <ScoreLine label="Attribution" value={formatPct(source.attribution_score)} tone="bg-lilac-500" />
          </div>

          <p className="mb-1.5 mt-3.5 text-[11px] font-semibold uppercase tracking-wider text-ink-faint">
            Excerpt relied upon
          </p>
          <blockquote className="max-h-44 overflow-y-auto rounded-xl border border-line bg-surface p-3 font-mono text-[11.5px] leading-relaxed text-ink-soft">
            {source.excerpt || "No abstract available."}
          </blockquote>

          {source.authors.length > 0 && (
            <p className="mt-3 text-[11.5px] text-ink-muted">
              {source.authors.slice(0, 6).join(", ")}
              {source.authors.length > 6 ? " et al." : ""}
            </p>
          )}

          {source.cited_by.length > 0 ? (
            <div className="mt-3 rounded-xl border border-mint-200 bg-mint-50 px-3 py-2">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-mint-700">
                Cited in support of
              </p>
              <p className="mt-1 text-[12.5px] leading-relaxed text-ink-soft">
                {source.cited_by.join(" · ")}
              </p>
            </div>
          ) : (
            <p className="mt-3 text-[11.5px] text-ink-faint">
              Retrieved by the search but not cited by any hypothesis.
            </p>
          )}

          {source.pmid_url && (
            <a
              href={source.pmid_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-ink px-3.5 py-1.5 text-[12px] font-medium text-surface transition-opacity hover:opacity-90"
            >
              Open PubMed record
              <svg viewBox="0 0 12 12" className="h-3 w-3" fill="none" stroke="currentColor" strokeWidth="1.6">
                <path d="M4 2h6v6M10 2L2.5 9.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </a>
          )}
        </div>
      )}
    </article>
  );
}

function ScoreLine({ label, value, tone }: { label: string; value: string; tone: string }) {
  const numeric = pct(parseFloat(value)) || 0;
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] uppercase tracking-wide text-ink-faint">{label}</span>
        <span className="font-mono text-[12px] text-ink-soft">{value}</span>
      </div>
      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-track">
        <div className={cx("h-full rounded-full", tone)} style={{ width: `${numeric * 100}%` }} />
      </div>
    </div>
  );
}

/* ── F. Explainable AI ──────────────────────────────────────────────────── */

export function XaiPanel({ result }: { result: AnalysisResponse }) {
  const xai = result.xai;
  if (!xai) return null;

  const indexById = new Map(result.evidence.map((e) => [e.source_id, e.citation_index]));
  const ranked = Object.entries(xai.retrieval_attribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);
  const cf = xai.counterfactual_explanation;

  return (
    <div className="space-y-3">
      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <Card
          title="Retrieval attribution"
          subtitle="How much each retrieved source contributed"
          tone="lilac"
        >
          {ranked.length === 0 ? (
            <p className="py-4 text-center text-[12.5px] text-ink-muted">No attribution data.</p>
          ) : (
            <div className="space-y-1">
              {ranked.map(([docId, score]) => (
                <BarRow
                  key={docId}
                  label={indexById.has(docId) ? `Source ${indexById.get(docId)}` : truncate(docId, 20)}
                  value={score}
                  tone="bg-lilac-500"
                />
              ))}
            </div>
          )}

          {cf && (
            <div className="mt-4 rounded-xl border border-lilac-200 bg-surface p-3">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-lilac-700">
                Counterfactual &mdash; if the strongest source were removed
              </p>
              <div className="mt-2 grid grid-cols-3 gap-3 text-center">
                <Metric label="Current" value={formatPct(cf.confidence_before)} />
                <Metric label="Without it" value={formatPct(cf.confidence_without_source)} />
                <Metric
                  label="Sensitivity"
                  value={`${(cf.confidence_delta ?? 0) >= 0 ? "+" : "−"}${Math.abs((cf.confidence_delta ?? 0) * 100).toFixed(1)} pts`}
                  tone={(cf.confidence_delta ?? 0) < 0 ? "text-blush-700" : "text-mint-700"}
                />
              </div>
              <p className="mt-2 text-[11.5px] leading-relaxed text-ink-faint">
                A drop here is the expected result, not an error. It quantifies how far the
                answer leans on its single strongest source: a small drop means the conclusion
                is robust, a large drop means it is evidence-sensitive.
              </p>
              {cf.verdict && (
                <p className="mt-2.5 border-t border-lilac-200 pt-2 text-[12px] leading-relaxed text-ink-muted">
                  {cf.verdict}
                </p>
              )}
            </div>
          )}
        </Card>

        <div className="space-y-3">
          <Card title="Grounding" subtitle="Are the claims supported?" tone="sky">
            <div className="space-y-3">
              <div>
                <div className="flex items-baseline justify-between">
                  <span className="text-[12px] text-ink-muted">Faithfulness</span>
                  <span className="text-[18px] font-semibold text-ink">
                    {xai.faithfulness_score !== null ? formatPct(xai.faithfulness_score) : "n/a"}
                  </span>
                </div>
                <div className="mt-1.5">
                  <Meter
                    value={xai.faithfulness_score ?? 0}
                    tone={(xai.faithfulness_score ?? 0) >= 0.6 ? "bg-mint-500" : "bg-butter-500"}
                  />
                </div>
                <p className="mt-1 text-[11px] text-ink-faint">Lexical grounding in the retrieved text</p>
              </div>

              <div className="flex items-center justify-between border-t border-sky-200 pt-2.5">
                <span className="text-[12px] text-ink-muted">Consistency check</span>
                {xai.consistency_check === null ? (
                  <span className="text-[12px] text-ink-faint">n/a</span>
                ) : (
                  <Badge tone={xai.consistency_check ? "mint" : "blush"}>
                    {xai.consistency_check ? "Pass" : "Fail"}
                  </Badge>
                )}
              </div>

              <div className="flex items-center justify-between border-t border-sky-200 pt-2.5">
                <span className="text-[12px] text-ink-muted">Confidence estimate</span>
                <span className="font-mono text-[12px] text-ink-soft">
                  {formatPct(xai.confidence_estimate)}
                </span>
              </div>

              <div className="flex items-center justify-between border-t border-sky-200 pt-2.5">
                <span className="text-[12px] text-ink-muted">Claims inspected</span>
                <span className="font-mono text-[12px] text-ink-soft">{xai.claims.length}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {xai.unsupported_claims.length > 0 && (
        <Card
          title="Claims lacking citation support"
          subtitle="Generated but not grounded in the retrieved literature"
          tone="blush"
        >
          <ul className="space-y-1.5">
            {xai.unsupported_claims.map((claim, i) => (
              <li key={i} className="flex gap-2 text-[12.5px] leading-relaxed text-ink-soft">
                <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-blush-500" />
                {claim}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div>
      <p className="text-[10.5px] uppercase tracking-wide text-ink-faint">{label}</p>
      <p className={cx("mt-0.5 font-mono text-[14px] font-semibold text-ink", tone)}>{value}</p>
    </div>
  );
}

/* ── G. Trust metrics ───────────────────────────────────────────────────── */

export function TrustPanel({ result }: { result: AnalysisResponse }) {
  const trust = result.trust_metrics;
  if (!trust) return null;

  const overall = trust.overall_trust_score ?? 0;
  const tone = levelTone(
    overall >= 0.7 ? "high" : overall >= 0.45 ? "medium" : "low",
  );

  return (
    <div className="space-y-3">
      <div className="grid gap-4 lg:grid-cols-[1fr_1.5fr]">
        <Card title="Overall trust" tone={overall >= 0.7 ? "mint" : overall >= 0.45 ? "butter" : "blush"}>
          <div className="flex flex-col items-center gap-3">
            <RadialGauge value={overall} label={trust.overall_label ?? "Trust"} />
            <p className="text-center text-[12px] leading-relaxed text-ink-muted">
              {overall >= 0.7
                ? "Evidence is current, relevant and properly cited."
                : overall >= 0.45
                  ? "Partially supported. Treat the leading hypothesis as provisional."
                  : "Low trust. Treat all output as insufficiently supported."}
            </p>
          </div>
        </Card>

        <Card title="Trust components" subtitle="Each computed from this case only" tone="lilac">
          <div className="space-y-1">
            <BarRow label="Source reliability" value={trust.source_reliability ?? 0} tone="bg-sky-500" />
            <BarRow label="Citation validity" value={trust.citation_validity ?? 0} tone="bg-mint-500" />
            <BarRow label="Grounded claims" value={trust.grounded_claim_rate ?? 0} tone="bg-lilac-500" />
            <BarRow label="Evidence relevance" value={trust.evidence_relevance ?? 0} tone="bg-butter-500" />
          </div>

          {Object.keys(trust.checklist).length > 0 && (
            <div className="mt-4 border-t border-lilac-200 pt-3">
              <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-lilac-700">
                Audit checklist
              </p>
              <ul className="grid gap-1.5 sm:grid-cols-2">
                {Object.entries(trust.checklist).map(([key, value]) => (
                  <li
                    key={key}
                    className="flex items-center justify-between gap-2 rounded-lg bg-surface px-3 py-1.5"
                  >
                    <span className="text-[12px] text-ink-muted">{titleCase(key)}</span>
                    {typeof value === "boolean" ? (
                      <Badge tone={value ? "mint" : "blush"}>{value ? "Pass" : "Flag"}</Badge>
                    ) : (
                      <span className="font-mono text-[12px] text-ink-soft">{formatPct(Number(value))}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      </div>

      {trust.abstain_status && (
        <div className="rounded-2xl border border-butter-200 bg-butter-50 p-4 shadow-card">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-butter-700">Abstention</p>
          <p className="mt-1 text-[13.5px] font-medium text-ink">
            Confidence fell below the configured threshold.
          </p>
          <p className="mt-1 text-[12.5px] leading-relaxed text-ink-muted">
            The system is signalling that the retrieved evidence does not support a reliable
            hypothesis. Treat the results above as insufficiently supported.
          </p>
        </div>
      )}
    </div>
  );
}