"""Setup script: download data and build indexes."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    print("=" * 60)
    print("Clinical Intelligence System - Setup")
    print("=" * 60)

    # Step 1: Download data
    print("\n[1/3] Downloading PubMed abstracts...")
    t0 = time.time()
    from download_data import download_pubmed_data
    docs = download_pubmed_data("./data")
    print(f"Downloaded {len(docs)} abstracts in {time.time() - t0:.1f}s")

    if len(docs) < 1000:
        print(f"WARNING: Only {len(docs)} abstracts downloaded (target: 1000+)", file=sys.stderr)

    # Step 2: Build indexes
    print("\n[2/3] Building FAISS and BM25 indexes...")
    t0 = time.time()
    from build_index import build_indexes
    n_docs, n_faiss, n_bm25 = build_indexes("./data/corpus.jsonl", "./data/faiss_index", "./data/corpus_bm25.pkl")
    print(f"Built indexes in {time.time() - t0:.1f}s")
    print(f"  Documents: {n_docs}, FAISS vectors: {n_faiss}, BM25 docs: {n_bm25}")

    # Step 3: Verify
    print("\n[3/3] Verifying setup...")
    import os
    checks = [
        ("Corpus JSONL", "./data/corpus.jsonl"),
        ("FAISS index", "./data/faiss_index.index"),
        ("FAISS docs", "./data/faiss_index.docs.pkl"),
        ("BM25 index", "./data/corpus_bm25.pkl"),
    ]
    all_ok = True
    for name, path in checks:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"  {name}: {'OK' if exists else 'MISSING'} ({size} bytes)")
        if not exists:
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok and n_docs >= 1000:
        print("Setup complete! Run: python run.py")
    else:
        print("Setup incomplete. Check warnings above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
