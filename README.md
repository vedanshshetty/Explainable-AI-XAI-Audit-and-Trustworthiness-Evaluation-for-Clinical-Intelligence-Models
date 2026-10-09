# Clinical Intelligence System

A research prototype for **retrieval-augmented clinical reasoning** with **explainable AI (XAI)** and **trust evaluation**. Given a clinical vignette it retrieves peer-reviewed literature, proposes differential hypotheses, cites every claim to a real document, and reports how far the answer can be trusted.

> **Research use only.** Not a medical device. Outputs are hypotheses for evaluation, never diagnoses.

---

## Contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [Troubleshooting: `ModuleNotFoundError`](#troubleshooting-modulenotfounderror)
- [Running it](#running-it)
- [Project layout](#project-layout)
- [How a request flows](#how-a-request-flows)
- [Citations](#citations)
- [XAI and trust metrics](#xai-and-trust-metrics)
- [Data and indexes](#data-and-indexes)
- [Privacy and safety](#privacy-and-safety)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)

---

## What it does

| Capability | Detail |
|---|---|
| **Hybrid retrieval** | Dense (FAISS) + lexical (BM25), fused with Reciprocal Rank Fusion |
| **Reranking** | Cross-encoder `ms-marco-MiniLM-L-6-v2` re-ranks the fused candidates |
| **Hypotheses** | Differential diagnoses with confidence bands, supporting / against factors, suggested workup |
| **Safety flags** | `critical` / `warning` / `info`, with explicit escalation wording |
| **Citations** | Every claim carries a `[Source N]` marker resolved to a real document |
| **Attribution** | Per-source relevance and attribution, plus which hypotheses each source supports |
| **Explainability** | Retrieval attribution, faithfulness, consistency, counterfactual sensitivity |
| **Trust metrics** | Source reliability, citation validity, grounded-claim rate, evidence relevance, abstention |
| **Privacy** | PHI redaction for SSN, MRN, phone, DOB, address and person names |

The design principle is **verifiable attribution**: rather than asking the model to be careful with citations, the system counts the markers it emits, resolves each against what was actually retrieved, and deletes any that do not resolve.

---

## Quick start

### Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | Tested on 3.11 (venv) and 3.14 (system) |
| Node.js | 18+ | Only for the React frontend |
| RAM | 8 GB+ | Loading the embedding and rerank models |
| OpenRouter key | — | All LLM calls go through it; there is no local model |

### 1. Install

```bash
cd clinical-intelligence-system

python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt
pip install -e .                 # editable install - see the note below

cp .env.example .env             # Windows: copy .env.example .env
# then edit .env and set OPENROUTER_API_KEY
```

`pip install -e .` puts the project root on `sys.path`, which makes the package
importable from **any** working directory. It prevents the
[`ModuleNotFoundError`](#troubleshooting-modulenotfounderror) described below.

### 2. Prepare data and indexes

The local corpus is the primary source, so a fresh clone needs no network access:

```bash
python scripts/build_index.py     # builds FAISS + BM25 from data/corpus.jsonl
```

If `data/corpus.jsonl` is missing:

```bash
python scripts/verify.py --gate V2   # generates a 1,200-document synthetic corpus
python scripts/build_index.py
```

To pull real abstracts from Europe PMC:

```bash
python scripts/download_data.py --refresh     # merge into the local corpus
python scripts/build_index.py                # REQUIRED after any corpus change
```

---

## Troubleshooting: `ModuleNotFoundError`

If you see:

```
ModuleNotFoundError: No module named 'backend'
```

and the log says uvicorn is watching `...\backend`, your terminal's working
directory is the **`backend/` folder**, not the project root. Uvicorn inherits
the working directory, so `backend` cannot be imported from inside itself.

Any one of these fixes it:

```bash
# 1. Use the wrapper - works from anywhere
python run_backend.py

# 2. Move to the project root first
cd ..
python -m uvicorn backend.main:app --reload

# 3. Install the package once
pip install -e .
```

`run.py`, `run_backend.py` and the editable install each pin the working
directory or `sys.path`, so the problem cannot recur once one is in place.

---

## Running it

```bash
# Backend + Streamlit UI
python run.py

# Backend only, safe from any directory
python run_backend.py
python run_backend.py --reload
python run_backend.py --port 8080
```

| Service | URL |
|---|---|
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/api/v1/status |
| Streamlit UI | http://localhost:8501 |
| React UI | http://localhost:3000 |

### React frontend

```bash
cd frontend-next
npm install
npm run dev
```

Light and dark themes, switched from the header. See
[`frontend-next/README.md`](frontend-next/README.md).

The browser calls `/api/backend/*`, which Next rewrites to `localhost:8000/*`.
The FastAPI app only allows `localhost:8501` in CORS, so this proxy keeps the
request same-origin **without modifying the backend**.

```bash
BACKEND_URL=http://192.168.1.10:8000 npm run dev          # Linux / macOS
$env:BACKEND_URL="http://192.168.1.10:8000"; npm run dev  # PowerShell
```

### Streamlit frontend

```bash
python -m streamlit run frontend/app.py
```

Pure Python, no Node toolchain. Same result sections in a dark clinical theme.

---

## Project layout

```
clinical-intelligence-system/
  backend/
    main.py                 FastAPI app, endpoints, health probe
    app/
      config.py             Settings; paths anchored to the project root
      models.py             Pydantic response models
      privacy.py            PHI redaction
      rag_service.py        Retrieval, citations, XAI, trust
  frontend/
    app.py                  Streamlit UI
  frontend-next/            React + TypeScript + Tailwind UI
    app/                    layout, page, global CSS and theme tokens
    components/             Sidebar, Topbar, Dashboard, Results, Charts,
                            Anatomy, Motion, ThemeToggle, ui
    lib/                    types, api client, helpers, useTheme
  scripts/
    download_data.py        Europe PMC fetch (local corpus is primary)
    build_index.py          FAISS + BM25 construction and size check
    setup.py                Data and index bootstrap
    verify.py               Verification gates V1-V9
  tests/
    test_clinical_system.py
    system_integration_tests.py
  data/                     corpus.jsonl, indexes, llm_cache
  docs/                     setup_guide.md, demo_script.md, protocol.md
  run.py                    Backend + Streamlit
  run_backend.py            Backend only, working-directory independent
  pyproject.toml            Editable install metadata
  requirements.txt
  .env.example
```

---

## How a request flows

```
POST /api/v1/analyze
  -> PHI-screened clinical text
  -> FAISS (k=20)  +  BM25 (k=20)
  -> Reciprocal Rank Fusion
  -> cross-encoder rerank (k=8)
  -> LLM prompt with numbered [Source N] blocks
  -> parse JSON
  -> resolve every citation marker against retrieved documents
  -> strip markers that do not resolve
  -> attribution, faithfulness, counterfactual, trust
  -> AnalysisResponse
```

`lib/types.ts` in the React frontend is a hand-maintained mirror of the response
schema. Update it whenever the backend response changes.

---

## Citations

The prompt requires inline `[Source N]` markers. After generation,
`_analyze_citations` resolves each marker against the documents actually
retrieved and **removes any that do not resolve**, so a hallucinated
`[Source 9]` can never reach the user.

| Field | Meaning |
|---|---|
| `citations_used` | Markers emitted, counted before stripping |
| `citation_validity` | Share of markers that resolved to a real record |
| `citation_coverage` | Share of retrieved sources that were cited |
| `evidence[].cited` | Whether the model cited this source |
| `evidence[].cited_by` | Which hypotheses it supports |
| `evidence[].attribution_score` | Rank, citation use and rerank score, blended |
| `evidence[].pmid_url` | PubMed link, **only** for genuine `pubmed_` records |

`pmid_url` is deliberately `null` for locally generated records. Those carry
synthetic identifiers (`doc_0001`, `PMID1234567`); linking them would send a
reader to an unrelated real paper. Refresh from Europe PMC for live links.

---

## XAI and trust metrics

| Metric | How it is computed |
|---|---|
| Retrieval attribution | Blended rank position, whether cited, rerank score |
| Faithfulness | Share of claim content words present in retrieved text (lexical grounding, no NLI model needed) |
| Consistency | Case vocabulary overlap with the top retrieved sources |
| Counterfactual | Confidence if the strongest source were removed |
| Citation validity | Share of markers resolving to real documents |
| Grounded claim rate | Share of claims with a citation or adequate grounding |
| Source reliability | Recency weighting of the retrieved literature |
| Abstention | Set when confidence falls below `ABSTAIN_CONFIDENCE_THRESHOLD` |

Faithfulness uses transparent lexical grounding rather than the NLI model, so the
figure is reproducible and cannot fail mid-demonstration.

Trust score blend:

```
0.25 * source_reliability + 0.25 * citation_validity
      + 0.20 * grounded_claim_rate + 0.30 * confidence
```

### Reading the counterfactual

The counterfactual panel shows a **negative** figure by design: it reports how
much confidence falls when the single strongest source is removed. A small drop
means the conclusion is robust; a large drop means it is evidence-sensitive. It
is a sensitivity measurement, not an error.

---

## Data and indexes

### Corpus

`data/corpus.jsonl`, one JSON object per line:

```json
{"id": "pubmed_30302954", "title": "Sepsis: Early Recognition and Optimized Treatment",
 "authors": ["Kim HI", "Park S"], "journal": "Tuberculosis and respiratory diseases",
 "year": 2019, "pmid": "30302954", "text": "..."}
```

The schema is identical whether records come from Europe PMC or are generated
locally, so `scripts/build_index.py` never changes.

### Index integrity

| File | Purpose |
|---|---|
| `corpus.jsonl` | Source documents |
| `faiss_index.index` / `.docs.pkl` | Dense vectors and id mapping |
| `corpus_bm25.pkl` | Lexical index |
| `llm_cache/` | Cached LLM responses |

If the corpus grows without a rebuild, the new documents are silently
unretrievable. Three guards catch this:

- `scripts/build_index.py` exits non-zero on a size mismatch.
- The service logs a warning at startup.
- `/api/v1/status` returns `index_in_sync`.

```bash
curl http://localhost:8000/api/v1/status
```

```json
{"status": "healthy", "corpus_docs": 2623, "indexed_docs": 2623, "index_in_sync": true}
```

---

## Privacy and safety

PHI is redacted before any outbound call:

| Type | Example | Replacement |
|---|---|---|
| SSN | `123-45-6789` | `[REDACTED]` |
| Phone | `555-123-4567` | `[REDACTED]` |
| MRN | `A1234567` | `[REDACTED]` |
| DOB | `1990-01-15` | `[REDACTED]` |
| Address | `12 High Street` | `[REDACTED]` |
| Person name | `John Smith` | `[REDACTED]` |

Safety flags escalate rather than diagnose. A `critical` flag is surfaced
prominently in both frontends with explicit escalation wording.

---

## Configuration

Copy `.env.example` to `.env`.

| Variable | Default | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | - | **Required** for all LLM calls |
| `OPENROUTER_MODEL` | `google/gemini-2.5-flash-lite` | Generation model |
| `OPENROUTER_TEMPERATURE` | `0.0` | Deterministic output |
| `RAG_K_RETRIEVE` | `20` | Candidates per retriever |
| `RAG_K_RERANK` | `8` | Documents kept after reranking |
| `CITATION_TOP_K` | `5` | Sources shown per answer |
| `ABSTAIN_CONFIDENCE_THRESHOLD` | `0.45` | Below this the system abstains |
| `EUROPE_PMC_BASE_URL` | `https://www.ebi.ac.uk/europepmc/webservices/rest` | Literature API |
| `EUROPE_PMC_EMAIL` | - | Contact address for polite access |
| `EUROPE_PMC_REQUEST_DELAY` | `1.0` | Seconds between requests |

`CORPUS_PATH`, `FAISS_INDEX_PATH` and `LLM_CACHE_DIR` resolve against the
**project root**, not the working directory, so behaviour is identical from anywhere.

---

## Testing

```bash
pytest tests/test_clinical_system.py -v
python tests/system_integration_tests.py
python scripts/verify.py --all
python scripts/verify.py --gate V4

cd frontend-next && npm run typecheck && npm run build
```

| Gate | Name | Checks |
|---|---|---|
| V1 | Clean install | Dependencies, imports, pytest |
| V2 | Data and indexes | Corpus size, index construction, coverage |
| V3 | Backend API | Analyze endpoint contract |
| V4 | XAI and trust | Metrics present, no hardcoded scores |
| V5 | Privacy | PHI redaction and injection resistance |
| V6 | UI | Frontend imports cleanly |
| V7 | Protocol | Evaluation documentation present |
| V8 | Documentation | README and guides present |
| V9 | Fresh clone | `.env` untracked, no large tracked files |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'backend'` | Wrong working directory | `pip install -e .`, or use `run_backend.py` |
| `[WinError 10013]` on port 8000 | Port already bound | Stop the other process; run one server at a time |
| Port 8000 bound but not answering | Windows accept-loop bug | Fixed in `backend/main.py` (selector loop) |
| `corpus_docs: 0` | Wrong working directory | Fixed: paths anchored to project root |
| `index_in_sync: false` | Corpus changed without rebuild | `python scripts/build_index.py` |
| React shows "Backend offline" | Backend not running | Start it, or set `BACKEND_URL` |
| React CORS error | Calling the backend directly | Use `/api/backend/*` |
| Empty retrieval | Indexes missing | `python scripts/build_index.py` |
| Low citation validity | Model emitting invalid markers | Tighten `SYSTEM_PROMPT` in `backend/app/rag_service.py` |

---

## Limitations

Stated plainly, because they matter for how results should be read.

1. **No clinical validation.** No prospective study, no expert panel, no outcome data.
2. **Faithfulness is lexical, not semantic.** It over-credits paraphrase and
   under-credits exact phrasing that shares no vocabulary. `NLI_MODEL` is
   configured but not loaded.
3. **Confidence is the model's own estimate.** It is not calibrated and should
   not be read as a probability.
4. **Trust weights are heuristic.** Chosen for interpretability, not fitted
   against expert judgement.
5. **Safety flags are model-generated.** Recall is unmeasured against a
   labelled emergency set.
6. **Retrieval is bounded by the indexed corpus.**

---

## Acknowledgments

OpenRouter (LLM access), Europe PMC (literature), Hugging Face and Sentence
Transformers (embeddings), FAISS (vector search), Rank BM25 (lexical search),
FastAPI, Streamlit, Next.js and Tailwind CSS.

---

**Disclaimer:** Research use only. Not a medical device and not for clinical
decision-making. Consult a qualified clinician.