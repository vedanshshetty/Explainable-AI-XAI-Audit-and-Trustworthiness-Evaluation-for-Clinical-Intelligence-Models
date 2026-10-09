"""Build FAISS and BM25 indexes from corpus."""

import json
import os
import pickle
import re
import sys
from pathlib import Path

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.config import settings

logger = structlog.get_logger(__name__)


def build_indexes(corpus_path, faiss_path, bm25_path):
    """Build FAISS and BM25 indexes from JSONL corpus."""
    corpus = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    corpus.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    logger.info("Building indexes", n=len(corpus))

    # Build FAISS index
    embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    texts = [d.get("text", "") for d in corpus]
    embeddings = embedder.encode(texts, convert_to_numpy=True)

    import faiss
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype(np.float32))

    docs_dict = {}
    idx_to_id = {}
    for i, doc in enumerate(corpus):
        docs_dict[doc["id"]] = doc
        idx_to_id[i] = doc["id"]

    Path(faiss_path).parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, f"{faiss_path}.index")
    with open(f"{faiss_path}.docs.pkl", "wb") as f:
        pickle.dump({"docs": docs_dict, "idx_to_id": idx_to_id}, f)
    logger.info("FAISS index saved", n=index.ntotal)

    # Build BM25 index
    try:
        import nltk
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab", quiet=True)
    except Exception:
        pass

    from rank_bm25 import BM25Okapi
    tokenized = [re.findall(r'\b\w+\b', d.get("text", "").lower()) for d in corpus]
    bm25 = BM25Okapi(tokenized)
    doc_ids = [d["id"] for d in corpus]

    with open(bm25_path, "wb") as f:
        pickle.dump({"bm25": bm25, "doc_ids": doc_ids}, f)
    logger.info("BM25 index saved", n=len(doc_ids))

    return len(corpus), index.ntotal, len(doc_ids)


def _index_health(corpus_path, faiss_path, bm25_path):
    """Report whether the built indexes cover every document in the corpus.

    A corpus that grew without a rebuild leaves documents permanently
    unretrievable, which looks like a silent quality regression rather than an
    error. Report it instead of letting it pass unnoticed.
    """
    corpus_size = sum(1 for line in open(corpus_path, "r", encoding="utf-8") if line.strip())
    index_path = f"{faiss_path}.index"
    if not os.path.exists(index_path):
        return corpus_size, 0, 0
    try:
        import pickle
        with open(f"{faiss_path}.docs.pkl", "rb") as f:
            n_faiss = len(pickle.load(f)["docs"])
    except Exception:
        n_faiss = 0
    try:
        import pickle
        with open(bm25_path, "rb") as f:
            n_bm25 = len(pickle.load(f)["doc_ids"])
    except Exception:
        n_bm25 = 0
    return corpus_size, n_faiss, n_bm25


if __name__ == "__main__":
    corpus_path = Path(settings.CORPUS_PATH)
    if not corpus_path.exists():
        print(f"ERROR: Corpus not found at {corpus_path}", file=sys.stderr)
        print("Run: python scripts/download_data.py", file=sys.stderr)
        sys.exit(1)

    faiss_path = settings.FAISS_INDEX_PATH
    # with_suffix() accepts only a single suffix, so compose the sibling filename
    # directly: data/corpus.jsonl -> data/corpus_bm25.pkl
    bm25_path = str(corpus_path.with_name(corpus_path.stem + "_bm25.pkl"))
    n_docs, n_faiss, n_bm25 = build_indexes(str(corpus_path), faiss_path, bm25_path)
    print(f"Built indexes: {n_docs} docs, {n_faiss} FAISS vectors, {n_bm25} BM25 docs")
    if n_faiss != n_docs or n_bm25 != n_docs:
        print("WARNING: Index sizes mismatch!", file=sys.stderr)

    # Fail loudly when the corpus outgrew the indexes.
    corpus_n, idx_faiss, idx_bm25 = _index_health(str(corpus_path), faiss_path, bm25_path)
    if corpus_n != idx_faiss or corpus_n != idx_bm25:
        print(
            f"ERROR: corpus has {corpus_n} documents but indexes cover "
            f"{idx_faiss} (FAISS) / {idx_bm25} (BM25). The extra documents cannot be "
            "retrieved. Re-run: python scripts/build_index.py",
            file=sys.stderr,
        )
        sys.exit(1)
