"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { StatusStrip, Topbar, type BackendState } from "@/components/Topbar";
import { Badge, Card, SectionHeading, Skeleton } from "@/components/ui";
import { Breathe, CountUp, PulseDot } from "@/components/Motion";
import {
  HypothesisPanel,
  ReasoningPanel,
  SafetyPanel,
  SourcesPanel,
  SummaryPanel,
  TrustPanel,
  XaiPanel,
} from "@/components/Results";
import { analyze, fetchStatus } from "@/lib/api";
import { SAMPLE_CASES, type AnalysisResponse, type ViewKey } from "@/lib/types";
import { cx } from "@/lib/utils";

const MIN_CASES = 10; // backend rejects shorter input
const LOADING_STEPS = [
  "Retrieving candidate documents",
  "Reranking with cross-encoder",
  "Analysing clinical evidence",
  "Generating hypotheses",
  "Resolving citations and trust",
];

export default function Dashboard() {
  const [text, setText] = useState("");
  const [view, setView] = useState<ViewKey>("analysis");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const [includeXai, setIncludeXai] = useState(true);
  const [includeTrust, setIncludeTrust] = useState(true);
  const [search, setSearch] = useState("");
  const [consented, setConsented] = useState(false);

  const [backend, setBackend] = useState<{
    state: BackendState;
    model?: string;
    corpus?: number;
    indexed?: number;
    inSync?: boolean;
  }>({ state: "checking" });

  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let alive = true;
    fetchStatus().then((status) => {
      if (!alive) return;
      setBackend(
        status
          ? {
              state: "ready",
              model: status.model,
              corpus: status.corpus_docs,
              indexed: status.indexed_docs,
              inSync: status.index_in_sync,
            }
          : { state: "offline" },
      );
    });
    return () => {
      alive = false;
    };
  }, []);

  const runSample = useCallback((id: string, value: string) => {
    setText(value);
    setActiveCaseId(id);
    setError(null);
  }, []);

  const runAnalysis = useCallback(async () => {
    const clinical = text.trim();
    if (clinical.length < MIN_CASES) {
      setError(`Please enter at least ${MIN_CASES} characters of clinical detail.`);
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingStep(0);
    const started = Date.now();

    // Advance the step label while the request is in flight.
    const ticker = setInterval(() => {
      setLoadingStep((s) => Math.min(s + 1, LOADING_STEPS.length - 1));
    }, 2600);

    try {
      const data = await analyze({
        clinical_text: clinical,
        include_xai: includeXai,
        include_trust: includeTrust,
        deep_mode: false,
      });
      setResult(data);
      setElapsed(Date.now() - started);
      setView("analysis");
      window.setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed unexpectedly.");
    } finally {
      clearInterval(ticker);
      setLoading(false);
    }
  }, [text, includeXai, includeTrust]);

  // Search filters the citation cards; nothing else is affected.
  const filteredEvidence = useMemo(() => {
    if (!result || search.trim().length < 2) return null;
    const q = search.toLowerCase();
    return result.evidence.filter((e) =>
      [e.title, e.journal, e.pmid ?? "", e.excerpt].join(" ").toLowerCase().includes(q),
    );
  }, [result, search]);

  if (!consented) {
    return (
      <ConsentGate
        onAccept={() => setConsented(true)}
      />
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-canvas">
      <Sidebar
        view={view}
        onViewChange={setView}
        onRunSample={runSample}
        activeCaseId={activeCaseId}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar
          state={backend.state}
          model={backend.model}
          corpus={backend.corpus}
          onSearch={setSearch}
        />

        <main className="min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[1240px] space-y-4 px-6 py-5">
            <StatusStrip
              state={backend.state}
              corpus={backend.corpus}
              indexed={backend.indexed}
              inSync={backend.inSync}
            />

            {/* ── Case input ─────────────────────────────────────────── */}
            <Card
              title="Clinical case"
              subtitle="Describe presentation, vital signs, examination findings and relevant history"
              action={
                <span className="rounded-full bg-canvas px-2.5 py-1 text-[11px] text-ink-faint">
                  {text.trim().length} chars
                </span>
              }
            >
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="e.g. 65-year-old male with three days of fever, productive cough and pleuritic chest pain. Temperature 38.9 C, HR 110, SpO2 92% on room air…"
                rows={5}
                className="w-full resize-y rounded-xl border border-line bg-canvas p-3.5 text-[13.5px] leading-relaxed text-ink placeholder:text-ink-faint focus:border-lilac-200 focus:bg-surface focus:outline-none focus:ring-2 focus:ring-lilac-100"
              />

              <div className="mt-3 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={runAnalysis}
                  disabled={loading}
                  className={cx(
                    "inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-[13.5px] font-semibold transition-all",
                    loading
                      ? "cursor-not-allowed bg-lilac-200 text-on-solid"
                      : "bg-lilac-500 text-on-solid shadow-lift hover:bg-lilac-700 active:scale-[0.98]",
                  )}
                >
                  {loading ? (
                    <svg viewBox="0 0 20 20" className="h-4 w-4 animate-spin" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="10" cy="10" r="7.5" opacity="0.25" />
                      <path d="M17.5 10A7.5 7.5 0 0010 2.5" strokeLinecap="round" />
                    </svg>
                  ) : (
                    <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M4 10h11M11 6l4 4-4 4" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  )}
                  {loading ? "Analyzing…" : "Analyze case"}
                </button>

                <label className="inline-flex cursor-pointer items-center gap-2 text-[12.5px] text-ink-muted">
                  <input
                    type="checkbox"
                    checked={includeXai}
                    onChange={(e) => setIncludeXai(e.target.checked)}
                    className="h-4 w-4 rounded border-line text-lilac-500 focus:ring-lilac-200"
                  />
                  Include explainable AI
                </label>
                <label className="inline-flex cursor-pointer items-center gap-2 text-[12.5px] text-ink-muted">
                  <input
                    type="checkbox"
                    checked={includeTrust}
                    onChange={(e) => setIncludeTrust(e.target.checked)}
                    className="h-4 w-4 rounded border-line text-lilac-500 focus:ring-lilac-200"
                  />
                  Include trust metrics
                </label>

                {text && !loading && (
                  <button
                    type="button"
                    onClick={() => {
                      setText("");
                      setActiveCaseId(null);
                      setError(null);
                    }}
                    className="ml-auto text-[12.5px] text-ink-faint underline-offset-2 hover:text-ink hover:underline"
                  >
                    Clear
                  </button>
                )}
              </div>

              {error && (
                <div className="mt-3 rounded-xl border border-blush-200 bg-blush-50 px-3.5 py-2.5">
                  <p className="text-[12.5px] leading-relaxed text-blush-700">{error}</p>
                </div>
              )}
            </Card>

            {/* ── Results ───────────────────────────────────────────── */}
            <div ref={resultsRef} className="space-y-5">
              {loading && <LoadingPanel step={loadingStep} />}

              {!loading && result && view === "analysis" && (
                <>
                  <SummaryPanel result={result} caseText={text} elapsed={elapsed} />

                  {result.safety_flags.length > 0 && (
                    <div>
                      <SectionHeading title="Safety flags" count={result.safety_flags.length} />
                      <SafetyPanel result={result} />
                    </div>
                  )}

                  <div>
                    <SectionHeading title="Condition hypotheses" count={result.condition_hypotheses.length} />
                    <HypothesisPanel result={result} />
                  </div>

                  <div>
                    <SectionHeading title="Differential reasoning" />
                    <ReasoningPanel result={result} />
                  </div>

                  <div>
                    <SectionHeading title="Sources & citations" count={result.evidence.length} />
                    <SourcesPanel result={result} />
                  </div>

                  {result.xai && (
                    <div>
                      <SectionHeading title="Explainable AI" />
                      <XaiPanel result={result} />
                    </div>
                  )}

                  {result.trust_metrics && (
                    <div>
                      <SectionHeading title="Trust metrics" />
                      <TrustPanel result={result} />
                    </div>
                  )}

                  <Footer result={result} />
                </>
              )}

              {!loading && result && view === "cases" && (
                <div className="space-y-3">
                  <SectionHeading
                    title="Sample cases"
                    count={SAMPLE_CASES.length}
                    hint="Load a case into the input"
                  />
                  <div className="grid gap-3 md:grid-cols-2">
                    {SAMPLE_CASES.map((sample) => (
                      <button
                        key={sample.id}
                        type="button"
                        onClick={() => {
                          runSample(sample.id, sample.text);
                          setView("analysis");
                        }}
                        className="rounded-2xl border border-line bg-surface p-4 text-left shadow-card transition-all hover:border-lilac-200 hover:shadow-lift"
                      >
                        <p className="text-[13.5px] font-semibold text-ink">{sample.label}</p>
                        <p className="mt-0.5 text-[11.5px] text-ink-faint">{sample.focus}</p>
                        <p className="mt-2 line-clamp-3 text-[12px] leading-relaxed text-ink-muted">
                          {sample.text}
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {!loading && result && view === "xai" && (
                <div className="space-y-3">
                  <SectionHeading title="Explainable AI" hint="Attribution, grounding and counterfactuals" />
                  {result.xai ? (
                    <XaiPanel result={result} />
                  ) : (
                    <Card>
                      <p className="text-[13px] text-ink-muted">
                        XAI was not requested for this analysis. Re-run with “Include explainable AI”
                        enabled.
                      </p>
                    </Card>
                  )}
                </div>
              )}

              {!loading && result && view === "trust" && (
                <div className="space-y-3">
                  <SectionHeading title="Trust evaluation" hint="Reliability of the evidence and the answer" />
                  {result.trust_metrics ? (
                    <TrustPanel result={result} />
                  ) : (
                    <Card>
                      <p className="text-[13px] text-ink-muted">
                        Trust metrics were not requested for this analysis. Re-run with “Include trust
                        metrics” enabled.
                      </p>
                    </Card>
                  )}
                </div>
              )}

              {!loading && !result && (
                <Card tone="lilac">
                  <div className="py-6 text-center">
                    <p className="animate-fade-up text-[14px] font-semibold text-ink">No analysis yet</p>
                    <p className="mx-auto mt-1.5 max-w-md text-[12.5px] leading-relaxed text-ink-muted">
                      Load one of the sample cases from the sidebar or write a clinical vignette, then
                      run the analysis to see hypotheses, citations, explainability and trust scores.
                    </p>
                    <div className="mt-4 flex flex-wrap justify-center gap-2">
                      {SAMPLE_CASES.slice(0, 4).map((sample) => (
                        <button
                          key={sample.id}
                          type="button"
                          onClick={() => runSample(sample.id, sample.text)}
                          className="rounded-full border border-lilac-200 bg-surface px-3.5 py-1.5 text-[12px] font-medium text-lilac-700 transition-colors hover:bg-lilac-100"
                        >
                          {sample.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </Card>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function LoadingPanel({ step }: { step: number }) {
  return (
    <div className="space-y-3">
      <Card
        title="Analyzing clinical evidence" tone="lilac"
        action={<PulseDot color="var(--lilac-500)" size={7} />}
      >
        <ol className="space-y-2">
          {LOADING_STEPS.map((label, i) => (
            <li key={label} className="flex items-center gap-2.5">
              {i < step ? (
                <span className="grid h-4 w-4 place-items-center rounded-full bg-mint-100 text-[9px] text-mint-700">
                  ✓
                </span>
              ) : i === step ? (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-lilac-200 border-t-lilac-500" />
              ) : (
                <span className="h-4 w-4 rounded-full border border-line" />
              )}
              <span
                className={cx(
                  "text-[12.5px]",
                  i === step ? "font-medium text-ink" : i < step ? "text-ink-muted" : "text-ink-faint",
                )}
              >
                {label}
              </span>
            </li>
          ))}
        </ol>
      </Card>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-[92px]" />
        ))}
      </div>
      <div className="grid gap-3 lg:grid-cols-[1.6fr_1fr]">
        <Skeleton className="h-[200px]" />
        <Skeleton className="h-[200px]" />
      </div>
    </div>
  );
}

function Footer({ result }: { result: AnalysisResponse }) {
  return (
    <footer className="flex flex-wrap items-center gap-x-3 gap-y-1 border-t border-line pt-3 text-[11.5px] text-ink-faint">
      <span className="font-mono">case {result.case_id}</span>
      <span>·</span>
      <span>{result.retrieval_count} documents retrieved</span>
      <span>·</span>
      <span>
        {result.model_used} via {result.provider ?? "unknown"}
      </span>
      <span>·</span>
      <span>{result.processing_time_ms} ms</span>
      <span className="ml-auto">
        <Badge tone="butter">Research only · not a medical device</Badge>
      </span>
    </footer>
  );
}

function ConsentGate({ onAccept }: { onAccept: () => void }) {
  return (
    <div className="grid min-h-screen place-items-center bg-canvas px-6 py-12">
      <div className="w-full max-w-lg">
        <div className="mb-5 flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-lilac-100 text-lilac-700">
            <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 12h3.2l2-5.4 3.4 11L15.6 12H21" />
            </svg>
          </span>
          <div>
            <p className="text-[17px] font-semibold tracking-tight text-ink">
              Clinical<span className="text-lilac-700">Intel</span>
            </p>
            <p className="text-[12px] text-ink-faint">Explainable clinical reasoning console</p>
          </div>
        </div>

        <Card title="Consent required" tone="lilac">
          <p className="text-[13.5px] leading-relaxed text-ink-soft">
            This is a research prototype, not a clinical device. Continuing acknowledges that:
          </p>
          <ul className="mt-3 space-y-2">
            {[
              "Case text is transmitted to a third-party hosted language model.",
              "Processing may occur outside your jurisdiction.",
              "Do not enter protected health information; the sample cases are synthetic.",
              "Results are hypotheses for evaluation, never diagnoses.",
            ].map((line) => (
              <li key={line} className="flex gap-2 text-[12.5px] leading-relaxed text-ink-muted">
                <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-lilac-500" />
                {line}
              </li>
            ))}
          </ul>

          <button
            type="button"
            onClick={onAccept}
            className="mt-5 w-full rounded-xl bg-lilac-500 px-5 py-2.5 text-[13.5px] font-semibold text-on-solid shadow-lift transition-all hover:bg-lilac-700 active:scale-[0.99]"
          >
            I consent and continue
          </button>
          <p className="mt-3 text-center text-[11.5px] text-ink-faint">
            Research use only. Not a medical device.
          </p>
        </Card>
      </div>
    </div>
  );
}