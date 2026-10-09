"""Download clinical literature abstracts from Europe PMC.

The local corpus (``data/corpus.jsonl``) is the *primary* source for this research
system.  Europe PMC (https://www.ebi.ac.uk/europepmc/) is a free, stable REST
service used only as an **optional refresh**; it returns abstracts, PMIDs,
journal titles and publication years in a single JSON response.

Design priorities, in order:
    1. Never destroy working local data.
    2. Never require the network for a normal run.
    3. Never break the index build path: output stays ``data/corpus.jsonl``
       in exactly the schema that ``scripts/build_index.py`` already expects.

NCBI eutils is intentionally no longer used: it is rate-limited and flaky.

Usage
-----
    python scripts/download_data.py                        # use local corpus (offline)
    python scripts/download_data.py --refresh              # merge Europe PMC into local
    python scripts/download_data.py --refresh --replace    # swap corpus entirely
    python scripts/download_data.py --topics "sepsis" "stroke" --refresh
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests


# ── Configuration ────────────────────────────────────────────────────────────

CLINICAL_TOPICS = [
    "myocardial infarction diagnosis",
    "acute stroke management",
    "sepsis early recognition",
    "pulmonary embolism diagnosis",
    "bacterial meningitis treatment",
    "diabetic ketoacidosis management",
    "acute appendicitis diagnosis",
    "ectopic pregnancy diagnosis",
    "type 2 diabetes mellitus guidelines",
    "hypertension treatment",
    "community-acquired pneumonia",
    "deep vein thrombosis prevention",
    "chronic obstructive pulmonary disease",
    "asthma exacerbation management",
    "seizure disorders diagnosis",
    "acute kidney injury",
    "spontaneous pneumothorax",
    "testicular torsion diagnosis",
    "hyperthyroidism treatment",
    "major depressive disorder",
    "social anxiety disorder prevalence",
    "postpartum depression screening",
    "attention deficit hyperactivity disorder diagnosis",
    "schizophrenia early intervention",
    "chronic kidney disease staging",
    "osteoporosis screening guidelines",
    "breast cancer screening mammography",
    "colorectal cancer screening colonoscopy",
    "prostate cancer PSA screening",
    "skin melanoma detection",
    "childhood vaccine adverse events",
    "opioid use disorder treatment",
    "antibiotic stewardship pneumonia",
    "informed consent clinical trials",
    "end of life care palliative",
    "telemedicine effectiveness rural",
    "healthcare worker burnout",
    "medical error reporting systems",
    "algorithmic bias clinical decision",
    "artificial intelligence diagnostic accuracy",
    "genomic medicine precision oncology",
]


def _setting(name: str, default):
    """Read a setting from the environment, then from backend settings, then default.

    Keeping this lazy means the script stays importable (and offline-usable) even
    when pydantic-settings is unavailable or the project root is not on sys.path.
    """
    raw = os.getenv(name)
    if raw not in (None, ""):
        return raw
    try:
        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from backend.app.config import settings
        return getattr(settings, name, default)
    except Exception:
        return default


def _setting_int(name: str, default: int) -> int:
    try:
        return int(_setting(name, default))
    except (TypeError, ValueError):
        return default


def _setting_float(name: str, default: float) -> float:
    try:
        return float(_setting(name, default))
    except (TypeError, ValueError):
        return default


EUROPE_PMC_BASE_URL = str(
    _setting("EUROPE_PMC_BASE_URL", "https://www.ebi.ac.uk/europepmc/webservices/rest")
).rstrip("/")
EUROPE_PMC_SEARCH_PATH = str(_setting("EUROPE_PMC_SEARCH_PATH", "search")).strip("/")
EUROPE_PMC_EMAIL = str(_setting("EUROPE_PMC_EMAIL", "dev@example.com"))
EUROPE_PMC_PAGE_SIZE = _setting_int("EUROPE_PMC_PAGE_SIZE", 100)
EUROPE_PMC_MAX_RETRIES = _setting_int("EUROPE_PMC_MAX_RETRIES", 3)
EUROPE_PMC_TIMEOUT = _setting_int("EUROPE_PMC_TIMEOUT", 30)
EUROPE_PMC_REQUEST_DELAY = _setting_float("EUROPE_PMC_REQUEST_DELAY", 1.0)

SEARCH_URL = f"{EUROPE_PMC_BASE_URL}/{EUROPE_PMC_SEARCH_PATH}"


# ── HTTP helpers ─────────────────────────────────────────────────────────────

def _headers() -> Dict[str, str]:
    """Polite, identifiable request headers (Europe PMC asks for a contact)."""
    return {
        "User-Agent": (
            "ClinicalIntelligenceSystem/1.0 "
            f"(academic research prototype; mailto:{EUROPE_PMC_EMAIL})"
        ),
        "Accept": "application/json",
    }


def _request_json(params: Dict[str, str], retries: int, timeout: int) -> Optional[dict]:
    """GET Europe PMC with exponential backoff. Returns None when the call fails."""
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            resp = requests.get(SEARCH_URL, params=params, headers=_headers(), timeout=timeout)
            if resp.status_code == 429 or resp.status_code >= 500:
                last_error = f"HTTP {resp.status_code}"
                # Respect Retry-After when the service provides it.
                wait = resp.headers.get("Retry-After")
                delay = float(wait) if (wait or "").isdigit() else (2 ** attempt)
                print(
                    f"  Europe PMC returned {resp.status_code}; retrying in {delay:.0f}s",
                    flush=True,
                )
                time.sleep(min(delay, 30.0))
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # network, DNS, JSON, HTTP error
            last_error = exc
            if attempt < max(1, retries) - 1:
                delay = 2 ** attempt
                print(f"  Europe PMC error ({exc}); retrying in {delay}s", flush=True)
                time.sleep(delay)
    print(f"  Europe PMC request failed after {retries} attempt(s): {last_error}", file=sys.stderr, flush=True)
    return None


# ── Record normalisation ─────────────────────────────────────────────────────

def _clean(value) -> str:
    """Collapse whitespace and strip stray XML/HTML fragments from Europe PMC text."""
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)          # Europe PMC may return markup
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", text).strip()


def _authors(record: dict) -> List[str]:
    """Prefer structured authorList; fall back to the authorString blob."""
    author_block = record.get("authorList") or {}
    people = author_block.get("author") or []
    names: List[str] = []
    if isinstance(people, list):
        for person in people[:12]:
            if not isinstance(person, dict):
                continue
            full = _clean(person.get("fullName"))
            if full:
                names.append(full)
                continue
            last = _clean(person.get("lastName"))
            initials = _clean(person.get("initials"))
            if last:
                names.append(f"{last} {initials}".strip())
    if names:
        return names
    raw = _clean(record.get("authorString"))
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()][:12]


def _year_of(record: dict) -> Optional[int]:
    journal_info = record.get("journalInfo") or {}
    for candidate in (record.get("pubYear"), journal_info.get("yearOfPublication")):
        if candidate in (None, ""):
            continue
        match = re.search(r"\d{4}", str(candidate))
        if match:
            return int(match.group(0))
    return None


def _record_to_doc(record: dict) -> Optional[dict]:
    """Map one Europe PMC result to the local corpus schema.

    Schema is identical to the existing corpus so scripts/build_index.py needs
    no change: id, title, authors, journal, year, pmid, abstract, text.
    """
    if not isinstance(record, dict):
        return None
    source = _clean(record.get("source")) or "MED"
    ext_id = _clean(record.get("id"))
    pmid = _clean(record.get("pmid"))
    if not pmid and source.upper() == "MED" and "/" in ext_id:
        pmid = ext_id.rsplit("/", 1)[-1].strip()
    abstract = _clean(record.get("abstractText"))
    if not pmid or not abstract:
        return None

    journal_info = record.get("journalInfo") or {}
    journal_title = (journal_info.get("journal") or {}).get("title")
    journal = _clean(journal_title) or _clean(record.get("bookOrReportDetails", {}).get("publisher"))

    return {
        "id": f"pubmed_{pmid}",
        "title": _clean(record.get("title")) or "Untitled",
        "authors": _authors(record),
        "journal": journal,
        "year": _year_of(record),
        "pmid": pmid,
        "abstract": abstract,
        "text": abstract,
        "source": "europe_pmc",
    }


# ── Europe PMC search ────────────────────────────────────────────────────────

def fetch_europe_pmc(
    query: str,
    max_results: int = 35,
    page_size: Optional[int] = None,
    retries: Optional[int] = None,
    timeout: Optional[int] = None,
    delay: Optional[float] = None,
) -> List[dict]:
    """Fetch up to ``max_results`` abstracts for ``query`` from Europe PMC.

    Uses cursor pagination so more than one page of results is retrievable
    without hammering the service. Returns [] on any unrecoverable failure.
    """
    page_size = max(1, min(page_size or EUROPE_PMC_PAGE_SIZE, 1000))
    retries = retries or EUROPE_PMC_MAX_RETRIES
    timeout = timeout or EUROPE_PMC_TIMEOUT
    delay = EUROPE_PMC_REQUEST_DELAY if delay is None else delay

    docs: List[dict] = []
    seen_ids = set()
    cursor = "*"

    while len(docs) < max_results:
        remaining = max_results - len(docs)
        window = min(page_size, remaining)
        params = {
            "query": f"({query})",
            "format": "json",
            "resultType": "core",       # core => abstractText, journalInfo, authorList
            "pageSize": str(window),
            "cursorMark": cursor,
        }
        payload = _request_json(params, retries=retries, timeout=timeout)
        if payload is None:
            break  # fall back to whatever we already collected

        results = ((payload.get("resultList") or {}).get("result")) or []
        if not results:
            break

        added = 0
        for record in results:
            doc = _record_to_doc(record)
            if doc and doc["id"] not in seen_ids:
                seen_ids.add(doc["id"])
                docs.append(doc)
                added += 1
                if len(docs) >= max_results:
                    break

        next_cursor = _clean(payload.get("nextCursorMark"))
        # Stop on the last page, a stalled cursor, or a page that added nothing.
        if not next_cursor or next_cursor == cursor or added == 0 or len(results) < window:
            break
        cursor = next_cursor
        time.sleep(delay)

    return docs[:max_results]


# Backwards-compatible alias: the old implementation targeted NCBI eutils.
def fetch_pubmed_abstracts(query: str, max_results: int = 35) -> List[dict]:
    """Deprecated alias kept for backwards compatibility; now hits Europe PMC."""
    return fetch_europe_pmc(query, max_results=max_results)


# ── Local corpus I/O ─────────────────────────────────────────────────────────

def load_local_corpus(corpus_file: Path) -> List[dict]:
    """Read data/corpus.jsonl, skipping malformed lines."""
    if not corpus_file.exists():
        return []
    docs: List[dict] = []
    with open(corpus_file, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(doc, dict) and doc.get("text"):
                docs.append(doc)
    return docs


def save_corpus(docs: List[dict], corpus_file: Path) -> None:
    """Atomically write the corpus so an interrupted run cannot truncate it."""
    corpus_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file = corpus_file.with_suffix(corpus_file.suffix + ".tmp")
    with open(tmp_file, "w", encoding="utf-8") as handle:
        for doc in docs:
            handle.write(json.dumps(doc, ensure_ascii=False) + "\n")
    os.replace(tmp_file, corpus_file)


def _merge(local: List[dict], remote: List[dict]) -> List[dict]:
    """Local corpus first (stable ordering), then unseen remote records."""
    merged: List[dict] = []
    seen = set()
    for doc in list(local) + list(remote):
        doc_id = doc.get("id")
        if not doc_id or doc_id in seen:
            continue
        seen.add(doc_id)
        merged.append(doc)
    return merged


# ── Orchestration ────────────────────────────────────────────────────────────

def _refresh_from_europe_pmc(
    corpus_file: Path,
    topics: List[str],
    max_per_topic: int,
    replace: bool,
) -> List[dict]:
    local = load_local_corpus(corpus_file)
    print(f"Europe PMC refresh over {len(topics)} topic(s): {SEARCH_URL}", flush=True)

    remote: List[dict] = []
    failed: List[str] = []
    for index, topic in enumerate(topics, 1):
        try:
            docs = fetch_europe_pmc(topic, max_results=max_per_topic)
        except Exception as exc:  # one bad topic must not kill the run
            print(f"  [{index}/{len(topics)}] '{topic}': failed ({exc})", file=sys.stderr, flush=True)
            failed.append(topic)
            continue
        remote.extend(docs)
        print(
            f"  [{index}/{len(topics)}] '{topic}': {len(docs)} abstract(s) "
            f"(running total {len(remote)})",
            flush=True,
        )
        if index < len(topics):
            time.sleep(EUROPE_PMC_REQUEST_DELAY)

    if not remote:
        if local:
            print(
                "Europe PMC returned nothing. Keeping the existing local corpus "
                "(no changes written).",
                file=sys.stderr,
                flush=True,
            )
            return local
        print(
            "Europe PMC unavailable and no local corpus exists. "
            "Run scripts/verify.py --gate V2 to generate a local corpus.",
            file=sys.stderr,
            flush=True,
        )
        return []

    final = remote if replace else _merge(local, remote)
    if local and not replace:
        backup = corpus_file.with_suffix(corpus_file.suffix + ".bak")
        try:
            save_corpus(local, backup)
            print(f"Backed up previous corpus to {backup}", flush=True)
        except Exception as exc:
            print(f"Warning: could not write backup ({exc})", file=sys.stderr, flush=True)

    save_corpus(final, corpus_file)
    print(
        f"\nSaved {len(final)} abstract(s) to {corpus_file} "
        f"({len(local)} local + {len(remote)} from Europe PMC, {len(failed)} topic(s) failed)",
        flush=True,
    )
    if len(final) != len(local):
        print(
            "Corpus changed. Rebuild the indexes before restarting the backend:\n"
            "    python scripts/build_index.py",
            flush=True,
        )
    return final


def download_pubmed_data(
    output_dir: str,
    topics: Optional[List[str]] = None,
    max_per_topic: int = 35,
    refresh_remote: bool = False,
    replace: bool = False,
) -> List[dict]:
    """Return the corpus for ``output_dir``, refreshing from Europe PMC on request.

    Priority:
      1. Local corpus exists and refresh_remote=False -> use it (no network).
      2. refresh_remote=True -> fetch Europe PMC, merge (or replace) locally.
      3. Remote failure -> fall back to the existing local corpus, unmodified.
    """
    topics = list(topics) if topics else list(CLINICAL_TOPICS)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    corpus_file = out_dir / "corpus.jsonl"

    if refresh_remote:
        return _refresh_from_europe_pmc(corpus_file, topics, max_per_topic, replace)

    local = load_local_corpus(corpus_file)
    if local:
        print(
            f"Using existing local corpus: {len(local)} document(s) at {corpus_file}\n"
            "(pass --refresh to optionally pull new abstracts from Europe PMC)",
            flush=True,
        )
        return local

    print(
        f"No local corpus at {corpus_file}; fetching from Europe PMC.",
        flush=True,
    )
    return _refresh_from_europe_pmc(corpus_file, topics, max_per_topic, replace)


# ── CLI ──────────────────────────────────────────────────────────────────────

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    default_corpus = str(_setting("CORPUS_PATH", "./data/corpus.jsonl"))
    parser = argparse.ArgumentParser(
        description="Prepare the local clinical corpus (local first, Europe PMC optional).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(default_corpus).parent),
        help="Directory holding corpus.jsonl (default: data/).",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Fetch abstracts from Europe PMC instead of only using the local corpus.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="With --refresh, replace the local corpus instead of merging into it.",
    )
    parser.add_argument(
        "--topics",
        nargs="*",
        default=None,
        help="Restrict the refresh to these search topics.",
    )
    parser.add_argument(
        "--max-per-topic",
        type=int,
        default=35,
        help="Maximum abstracts to fetch per topic (default: 35).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    docs = download_pubmed_data(
        output_dir=args.output_dir,
        topics=args.topics,
        max_per_topic=args.max_per_topic,
        refresh_remote=args.refresh,
        replace=args.replace,
    )
    if not docs:
        return 1
    print(f"Corpus ready: {len(docs)} document(s).", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())