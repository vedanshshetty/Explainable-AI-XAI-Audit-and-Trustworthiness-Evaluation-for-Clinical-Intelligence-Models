# Clinical Intelligence System - Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | Tested on 3.11 (venv) and 3.14 (system) |
| pip | latest | Ships with Python |
| Node.js | 18+ | **Optional**, only for the React frontend |
| RAM | 8 GB+ | Needed to load the embedding and rerank models |
| OpenRouter key | — | Required for all LLM calls; there is no local model |

---

## Installation

```bash
# 1. Get the code
git clone <repo-url>
cd clinical-intelligence-system

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Linux / macOS

# 3. Dependencies
pip install -r requirements.txt

# 4. Make the project importable from anywhere  <- important
pip install -e .

# 5. Environment variables
cp .env.example .env             # Windows: copy .env.example .env
# edit .env and set OPENROUTER_API_KEY
```

Step 4 is what prevents `ModuleNotFoundError: No module named 'backend'`. It
writes a path entry into site-packages so the `backend` package resolves
regardless of your working directory.

---

## Data setup

The local corpus is the primary source, so no network access is required.

```bash
# Build FAISS + BM25 from data/corpus.jsonl
python scripts/build_index.py
```

If `data/corpus.jsonl` does not exist:

```bash
# Generate a 1,200-document synthetic corpus and build indexes
python scripts/verify.py --gate V2
python scripts/build_index.py
```

### Optional: real literature from Europe PMC

```bash
# Merge real abstracts into the local corpus (backs up, then rebuilds)
python scripts/download_data.py --refresh

# Replace the corpus outright instead of merging
python scripts/download_data.py --refresh --replace

# Restrict to specific topics
python scripts/download_data.py --refresh --topics "sepsis early recognition" "acute stroke management"

# REQUIRED after any corpus change
python scripts/build_index.py
```

Notes:

- A plain `python scripts/download_data.py` makes **no** network call.
- `--refresh` never destroys working data: it writes a `.bak` first and
  falls back to the local corpus if Europe PMC is unreachable.
- Europe PMC replaced NCBI eutils, which is rate-limited and unreliable.

---

## Running the backend

Any of these works, from any directory:

```bash
python run_backend.py                # wrapper, cwd-independent
python run_backend.py --reload       # with auto-reload
python run_backend.py --port 8080    # custom port

python run.py                        # backend + Streamlit together

python -m uvicorn backend.main:app --reload    # requires the project root as cwd
```

Verify:

```bash
curl http://localhost:8000/api/v1/status
```

```json
{
  "status": "healthy",
  "model": "google/gemini-2.5-flash-lite",
  "corpus_docs": 2623,
  "indexed_docs": 2623,
  "index_in_sync": true
}
```

`index_in_sync: false` means the corpus grew without a rebuild — run
`python scripts/build_index.py`.

---

## Running a frontend

### React / Next.js (primary)

```bash
cd frontend-next
npm install
npm run dev              # http://localhost:3000
```

The browser calls `/api/backend/*`, which Next rewrites to
`http://localhost:8000/*`. This avoids CORS without touching the backend.

Point at a different backend:

```bash
BACKEND_URL=http://192.168.1.10:8000 npm run dev          # Linux / macOS
$env:BACKEND_URL="http://192.168.1.10:8000"; npm run dev # PowerShell
```

### Streamlit (fallback)

```bash
python -m streamlit run frontend/app.py --server.port 8501
```

---

## Tests

```bash
# Unit tests
pytest tests/test_clinical_system.py -v

# Integration tests (backend must already be running)
python tests/system_integration_tests.py

# Verification gates V1-V9
python scripts/verify.py --all
python scripts/verify.py --gate V3

# Frontend
cd frontend-next && npm run typecheck && npm run build
```

---

## If something is wrong

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'backend'` | `pip install -e .`, then retry |
| `[WinError 10013]` binding port 8000 | Another process holds the port; stop it |
| Port 8000 bound but not answering | Restart the backend; do not run two at once |
| `corpus_docs: 0` | Run `python scripts/build_index.py` |
| `index_in_sync: false` | `python scripts/build_index.py` |
| React shows "Backend offline" | Start the backend, or set `BACKEND_URL` |
| `OPENROUTER_API_KEY not set` | Copy `.env.example` to `.env` and add the key |