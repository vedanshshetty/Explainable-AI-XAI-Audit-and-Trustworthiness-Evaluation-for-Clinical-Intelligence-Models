"""Download PubMed data for the clinical intelligence system."""

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List

import requests


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


def fetch_pubmed_abstracts(query, max_results=40):
    """Fetch PubMed abstracts via NCBI E-utilities using plain requests."""
    from urllib.parse import urlencode
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    email = os.getenv("ENTREZ_EMAIL", "dev@example.com")

    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json", "email": email}
    url = base_url + "esearch.fcgi?" + urlencode(params)

    id_list = []
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])
            if id_list:
                break
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
    if not id_list:
        return []

    all_docs = []
    batch_size = 20
    for i in range(0, len(id_list), batch_size):
        batch = id_list[i:i + batch_size]
        fetch_params = {"db": "pubmed", "id": ",".join(batch), "retmode": "json", "rettype": "abstract", "email": email}
        fetch_url = base_url + "efetch.fcgi?" + urlencode(fetch_params)
        try:
            resp = requests.get(fetch_url, timeout=30)
            resp.raise_for_status()
            fetched = resp.json()
            papers = fetched.get("PubmedArticleSet", {}).get("PubmedArticle", [])
            for paper in papers:
                medline_cite = paper.get("MedlineCitation", {})
                article = medline_cite.get("Article", {})
                pmid = str(medline_cite.get("PMID", {}).get("#Text", ""))
                title = "".join(t for t in article.get("ArticleTitle", []) if isinstance(t, str))
                abstract_text = ""
                for ab in article.get("Abstract", {}).get("AbstractText", []):
                    if isinstance(ab, str):
                        abstract_text += ab + " "
                    elif isinstance(ab, dict):
                        abstract_text += ab.get("#Text", "") + " "
                journal = ""
                jt = article.get("Journal", {}).get("Title", "")
                journal = str(jt[0] if isinstance(jt, list) else jt)
                year = None
                date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                if isinstance(date, dict):
                    ys = date.get("Year", "")
                    if ys:
                        try:
                            year = int(ys)
                        except ValueError:
                            pass
                authors = []
                for al in article.get("AuthorList", []):
                    if isinstance(al, list):
                        for a in al:
                            if isinstance(a, dict):
                                last = a.get("LastName", "")
                                if last:
                                    authors.append(str(last))
                if pmid and abstract_text.strip():
                    all_docs.append({
                        "id": f"pubmed_{pmid}",
                        "title": title.strip(),
                        "journal": journal.strip(),
                        "year": year,
                        "pmid": pmid,
                        "authors": authors,
                        "text": abstract_text.strip(),
                    })
        except Exception as e:
            print(f"Error fetching batch {i//batch_size}: {e}", file=sys.stderr)
        time.sleep(0.5)
    return all_docs


def download_pubmed_data(output_dir, topics=None, max_per_topic=35):
    """Download PubMed abstracts for the given topics."""
    if topics is None:
        topics = CLINICAL_TOPICS
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    all_docs = []
    seen_ids = set()
    for topic in topics:
        docs = fetch_pubmed_abstracts(topic, max_results=max_per_topic)
        new_docs = [d for d in docs if d["id"] not in seen_ids]
        seen_ids.update(d["id"] for d in new_docs)
        all_docs.extend(new_docs)
        print(f"Topic '{topic}': {len(docs)} fetched, {len(new_docs)} new (total: {len(all_docs)})", flush=True)
        time.sleep(0.5)

    output_file = out_path / "corpus.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in all_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(all_docs)} abstracts to {output_file}", flush=True)
    return all_docs


if __name__ == "__main__":
    download_pubmed_data("./data")
