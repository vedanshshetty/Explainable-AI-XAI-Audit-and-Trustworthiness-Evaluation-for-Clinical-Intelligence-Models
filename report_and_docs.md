# Clinical Intelligence System - Final Report

> **Research use only.** Not a medical device and not for clinical
> decision-making. The figures below describe software behaviour on synthetic
> and public data; they are not clinical validation.

## Executive Summary

This report documents the design, verification and current limitations of a
clinical intelligence system that provides research-focused differential
diagnosis support using retrieval-augmented generation (RAG) with explainable
AI (XAI) and trust evaluation.

The central design decision is **verifiable attribution**. Rather than asking a
language model to "be careful about citations", the system counts the citation
markers the model emits, resolves each one against the documents actually
retrieved, and deletes any marker that does not resolve. A hallucinated
citation is therefore measurable rather than merely discouraged.

## System Components

### Backend (FastAPI)

- **Retrieval**: FAISS (dense) + BM25 (lexical), fused with Reciprocal Rank
  Fusion, then reranked by a cross-encoder. Configurable via `RAG_K_RETRIEVE`
  (20) and `RAG_K_RERANK` (8).
- **Generation**: OpenRouter-hosted LLM. Deterministic by default
  (`temperature=0.0`, fixed seed). No local model.
- **Citations**: `_analyze_citations` resolves `[Source N]` markers to
  retrieved records, strips unresolvable markers, and reports
  `citations_used`, `citation_validity` and `citation_coverage`.
- **XAI**: retrieval attribution, lexical faithfulness, consistency check,
  counterfactual confidence sensitivity, and unsupported-claim detection.
- **Trust**: source reliability, citation validity, grounded-claim rate,
  evidence relevance, an audit checklist and an abstention signal.
- **Privacy**: PHI redaction for SSN, phone, MRN, DOB, address and person name.

### Frontends

Two interchangeable interfaces over the same API:

- **React / Next.js** (`frontend-next/`) — primary. TypeScript, Tailwind,
  pastel clinical styling, inline SVG charts, expandable citation cards,
  original SVG anatomy artwork selected from case-text keywords.
- **Streamlit** (`frontend/app.py`) — fallback. Pure Python, dark clinical
  theme, no Node toolchain required.

The React app calls `/api/backend/*`, which Next rewrites to
`localhost:8000/*`. This circumvents the backend's CORS allow-list **without
modifying the backend**.

### Data

- Primary source: the local corpus at `data/corpus.jsonl`.
- Optional refresh: Europe PMC REST API. This replaced NCBI eutils, which is
  rate-limited and unreliable. Refreshes are opt-in, back up the previous
  corpus, and fall back cleanly if the service is unreachable.
- Index integrity is enforced: `build_index.py` exits non-zero on a size
  mismatch, the service warns at startup, and `/api/v1/status` exposes
  `index_in_sync`.

### Verification Framework

Automated gates V1-V9 covering imports, index integrity, API contract, XAI and
trust presence (including a check that no trust score is hardcoded), PHI
redaction, injection resistance, UI imports, documentation completeness and
clone hygiene.

## Verification Results

| Gate | Status | Notes |
|------|--------|-------|
| V1 | PASS | Dependencies, imports and unit tests valid |
| V2 | PASS | Corpus and FAISS/BM25 indexes constructed and in sync |
| V3 | PASS | Analyze endpoint returns a valid response |
| V4 | PASS | XAI and trust metrics present; no hardcoded scores |
| V5 | PASS | PHI redaction and injection resistance working |
| V6 | PASS | Both frontends import cleanly |
| V7 | PASS | Protocol and results directory present |
| V8 | PASS | README, setup guide, demo script and protocol present |
| V9 | PASS | `.env` untracked; no large tracked files |

Unit tests: 29 passing.

### Observed behaviour

Representative run (community-acquired pneumonia, 2,623-document corpus):

| Quantity | Observed |
|---|---|
| Leading hypothesis | Community-Acquired Pneumonia, high confidence |
| Citation validity | 1.00 (all emitted markers resolved) |
| Citation coverage | 1.00 |
| Trust score | 0.91 (High) |
| Counterfactual | Removing the top source drops confidence by ~0.24 |

These are single-run observations on one case, **not** an evaluation. See
`docs/protocol.md` for the intended protocol.

## Ethical Considerations

1. **Safety framing** — The system states in every interface that it is a
   research tool, not a medical device, and that outputs are hypotheses rather
   than diagnoses.
2. **Escalation over diagnosis** — A `critical` safety flag is surfaced
   prominently with explicit "contact a clinician" wording. The system never
   asserts a diagnosis.
3. **PHI protection** — Inputs are scanned and redacted before any outbound
   call. The consent gate discloses that text is sent to a third-party model
   hosted outside the user's jurisdiction.
4. **Injection resistance** — The safety rules in the system prompt are
   unconditional and the architecture refuses definitive diagnoses, drug
   names and dosages.
5. **Transparency** — Every claim is traceable to a retrieved record, and the
   exact excerpt relied upon is shown.
6. **Abstention** — Below the confidence threshold the system signals that the
   evidence does not support a reliable hypothesis rather than presenting a
   weak answer confidently.
7. **Honest citation links** — PubMed links are emitted only for records that
   genuinely came from PubMed. Synthetic local records display their PMID as
   plain text, because linking a fabricated identifier would direct a reader to
   an unrelated real paper.

## Known Limitations

1. **No clinical validation.** No prospective study, no expert panel, no
   outcome data. Nothing here supports clinical deployment.
2. **Faithfulness is lexical, not semantic.** Grounding is computed by content
   word overlap. It is reproducible and cannot fail mid-demonstration, but it
   will over-credit paraphrases and under-credit exact phrasing that shares no
   vocabulary. `NLI_MODEL` is configured but not loaded.
3. **Citation validity reflects model behaviour, not model quality.** Stripping
   invalid markers protects the user; the validity figure reports how often the
   model needed correcting.
4. **Trust metrics are heuristic.** The weights in the trust blend were chosen
   for interpretability, not fitted against expert judgement.
5. **Confidence is the model's own estimate.** It is not calibrated against
   ground truth and should not be read as a probability.
6. **Retrieval is bounded by the corpus.** Quality depends entirely on what has
   been indexed.
7. **Safety flags are model-generated.** Recall has not been measured against a
   labelled emergency set.

## Future Work

- Prospective evaluation against expert consensus using `docs/protocol.md`.
- Semantic faithfulness via the configured NLI model.
- Calibration of confidence against measured accuracy.
- Practitioner review of the safety-flag taxonomy.
- Retrieval evaluation with a labelled query set for Precision@k.

---

**Disclaimer:** Research use only. Not a medical device and not for clinical
decision-making. Consult a qualified clinician.