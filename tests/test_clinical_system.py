"""Tests for the clinical intelligence system using fixture corpus."""
import json
import os
import re
import sys
from pathlib import Path

import pytest
from pytest import mark

# Fixture corpus for retrieval tests
FIXTURE_DOCS = [
    {"id": "pubmed_1", "title": "Acute Myocardial Infarction Diagnosis and Management", "text": "Acute myocardial infarction (AMI) presents with substernal chest pain, diaphoresis, and ST elevation on ECG. Early diagnosis using cardiac troponin levels is critical.", "journal": "JACC", "year": 2022, "pmid": "1", "authors": ["Smith J", "Doe A"]},
    {"id": "pubmed_2", "title": "Ischemic Stroke: Diagnosis and Thrombolysis", "text": "Acute ischemic stroke presents with sudden focal neurological deficits. CT angiography and perfusion imaging guide thrombectomy decisions within 6-24 hours.", "journal": "NEJM", "year": 2023, "pmid": "2", "authors": ["Jones B", "Williams C"]},
    {"id": "pubmed_3", "title": "Sepsis: Early Recognition and Bundle", "text": "Sepsis is defined as life-threatening organ dysfunction due to infection. The sepsis bundle includes lactate measurement, blood cultures, and broad-spectrum antibiotics within 3 hours.", "journal": "Lancet", "year": 2021, "pmid": "3", "authors": ["Brown D", "Chen E"]},
    {"id": "pubmed_4", "title": "Type 2 Diabetes Management Guidelines", "text": "Type 2 diabetes mellitus diagnosis requires HbA1c >= 6.5% or fasting glucose >= 126 mg/dL. First-line therapy includes metformin and lifestyle modification.", "journal": "Diabetes Care", "year": 2022, "pmid": "4", "authors": ["Kim F", "Lopez G"]},
    {"id": "pubmed_5", "title": "Pulmonary Embolism: Wells Criteria and CT Angiography", "text": "Pulmonary embolism suspected with Wells criteria scoring. CT angiography is the gold standard diagnostic test showing filling defects in pulmonary vasculature.", "journal": "AJRCCM", "year": 2020, "pmid": "5", "authors": ["Wang H", "Singh I"]},
]


def test_fixture_corpus_loads():
    """Test that fixture corpus loads and has correct structure."""
    assert len(FIXTURE_DOCS) == 5
    for doc in FIXTURE_DOCS:
        assert "id" in doc
        assert "title" in doc
        assert "text" in doc
        assert "journal" in doc
        assert "pmid" in doc


def test_reciprocal_rank_fusion():
    """Test RRF fusion logic."""
    from backend.app.rag_service import reciprocal_rank_fusion
    ranks1 = ["a", "b", "c"]
    ranks2 = ["b", "a", "c", "d"]
    fused = reciprocal_rank_fusion([ranks1, ranks2], k=60)
    # b should be highest (rank 2 in both lists)
    assert "b" in fused
    # d should only be in second list
    assert "d" in fused
    # All should have positive scores
    assert all(v > 0 for v in fused.values())


def test_bm25_retriever():
    """Test BM25 retriever with fixture data."""
    from backend.app.rag_service import Bm25Retriever
    bm25 = Bm25Retriever()
    bm25.build_index(FIXTURE_DOCS)
    results = bm25.search("myocardial infarction chest pain", k=3)
    assert len(results) >= 1
    # The MI doc should be in results
    top_doc_ids = [r[0] for r in results]
    assert "pubmed_1" in top_doc_ids[:3]


def test_faiss_retriever_creation():
    """Test FAISS retriever can be created."""
    from backend.app.rag_service import FAISSRetriever
    faiss = FAISSRetriever(dim=384)
    assert faiss.ntotal == 0


def test_parse_llm_result_success():
    """Test parsing valid LLM output."""
    from backend.app.rag_service import RAGService
    valid_response = {
        "text": json.dumps({
            "summary": "Patient presentation consistent with AMI",
            "condition_hypotheses": [
                {"condition": "Acute MI", "confidence": 0.85, "confidence_level": "high",
                 "supporting_factors": ["chest pain", "ST elevation"]},
                {"condition": "Angina", "confidence": 0.3, "confidence_level": "low",
                 "supporting_factors": []}
            ],
            "differential_reasoning": "The presentation strongly suggests...",
            "safety_flags": [{"flag_type": "cardiac", "message": "Possible MI", "severity": "critical"}],
            "confidence_overall": 0.8
        })
    }
    parsed = RAGService._parse_llm_result(valid_response)
    assert "condition_hypotheses" in parsed
    assert len(parsed["condition_hypotheses"]) == 2
    assert parsed["condition_hypotheses"][0]["condition"] == "Acute MI"
    assert parsed["confidence_overall"] == 0.8


def test_parse_llm_result_json_embedded():
    """Test parsing LLM output with JSON embedded in text."""
    from backend.app.rag_service import RAGService
    text = 'Here is my analysis:\n{"summary": "Test", "condition_hypotheses": [], "confidence_overall": 0.5}\nEnd.'
    parsed = RAGService._parse_llm_result({"text": text})
    assert parsed["summary"] == "Test"


def test_parse_llm_result_invalid():
    """Test parsing invalid LLM output returns error flag."""
    from backend.app.rag_service import RAGService
    parsed = RAGService._parse_llm_result({"text": "This is not valid JSON at all"})
    assert parsed.get("error") == "parse_failed"


def test_privacy_redaction():
    """Test PHI redaction works."""
    from backend.app.privacy import redact_phi, detect_phi
    text = "Patient John Smith, SSN 123-45-6789, phone 555-123-4567, MRN A1234567"
    redacted, found = redact_phi(text)
    assert "123-45-6789" not in redacted
    assert "A1234567" not in redacted
    assert "John" not in redacted or "Smith" not in redacted  # At least some redaction
    # Should detect SSN and MRN at minimum
    assert len(found) > 0


def test_privacy_no_phi():
    """Test no PHI detection on clean text."""
    from backend.app.privacy import redact_phi, is_safe
    clean_text = "A 65-year-old male with fever and cough for 3 days."
    assert is_safe(clean_text)


def test_models_creation():
    """Test that models can be instantiated."""
    from backend.app.models import (
        ClinicalCaseRequest, AnalysisResponse, ConditionHypothesis,
        SafetyFlag, TrustMetrics, XAIExplanation, ConfidenceLevel,
    )
    req = ClinicalCaseRequest(clinical_text="Test case with sufficient length here")
    assert req.clinical_text == "Test case with sufficient length here"
    assert req.include_xai == True
    assert req.include_trust == True

    hyp = ConditionHypothesis(
        condition="Pneumonia", confidence=0.7, confidence_level=ConfidenceLevel.HIGH
    )
    assert hyp.condition == "Pneumonia"
    assert hyp.confidence == 0.7


def test_safety_flags():
    """Test safety flag creation."""
    from backend.app.models import SafetyFlag, SafetySeverity
    flag = SafetyFlag(flag_type="emergency", message="Possible MI", severity=SafetySeverity.CRITICAL)
    assert flag.severity == SafetySeverity.CRITICAL
    assert flag.message == "Possible MI"


def test_trust_metrics():
    """Test trust metrics creation."""
    from backend.app.models import TrustMetrics
    tm = TrustMetrics(
        source_reliability=0.8,
        overall_trust_score=0.7,
        overall_label="High",
    )
    assert tm.source_reliability == 0.8
    assert tm.overall_label == "High"


def test_rag_service_build_prompt():
    """Test that RAG prompt includes full document text."""
    from backend.app.rag_service import RAGService
    svc = RAGService()
    prompt = svc._build_rag_prompt("Test case", FIXTURE_DOCS[:2])
    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt
    assert "Acute Myocardial Infarction" in prompt  # Title
    assert "substernal chest pain" in prompt  # Abstract text
    assert len(prompt) > 500  # Should be substantial


def test_rag_service_trust_metrics():
    """Test trust metrics calculation."""
    from backend.app.rag_service import RAGService
    svc = RAGService()
    docs = [FIXTURE_DOCS[0]]
    parsed = {"confidence_overall": 0.6}
    trust = svc._calculate_trust_metrics(docs, parsed)
    assert trust.source_reliability >= 0.0
    assert trust.abstain_status == False  # 0.6 > 0.45
    assert trust.checklist is not None


def test_rag_service_abstention():
    """Test that low confidence triggers abstention."""
    from backend.app.rag_service import RAGService
    svc = RAGService()
    docs = [FIXTURE_DOCS[0]]
    parsed = {"confidence_overall": 0.2}
    trust = svc._calculate_trust_metrics(docs, parsed)
    assert trust.abstain_status == True  # 0.2 < 0.45


# --- Regression tests: PHI patterns must not silently stop matching ---
# These guard against double-escaping bugs in raw-string regexes (e.g. r'\\s'
# matching a literal backslash instead of whitespace), which make a PHI control
# fail open with no test failure.

PHI_MUST_DETECT = [
    ("SSN", "SSN 123-45-6789 assigned"),
    ("phone", "Call 555-123-4567 now"),
    ("DOB", "DOB 1990-01-15 recorded"),
    ("DOB_written", "Born on January 5, 1990 here"),
    ("person_name", "John Smith presented"),
    ("address", "Lives at 123 Main Street 45"),
    ("medical_record_number", "Patient ID: 4482910 on file"),
    ("medical_record_number", "MRN: A12345678 assigned"),
]

PHI_MUST_STAY_CLEAN = [
    "65-year-old male with chest pain radiating to left arm",
    "Fever, cough, and crackles on auscultation; RR 24, HR 102",
    "Patient reports shortness of breath since yesterday",
    "Laboratory results show elevated troponin at 0.9 ng/mL",
    "Symptoms include nausea vomiting and dizziness",
]


@mark.parametrize("expected_label,text", PHI_MUST_DETECT)
def test_privacy_detects_each_phi_type(expected_label, text):
    """Every advertised PHI type must actually be detected."""
    from backend.app.privacy import detect_phi
    found = detect_phi(text)
    assert found, f"no PHI detected in {text!r} (expected {expected_label})"
    assert expected_label in found, f"{text!r} -> {found}, missing {expected_label}"


@mark.parametrize("text", PHI_MUST_STAY_CLEAN)
def test_privacy_no_false_positives_on_clinical_text(text):
    """Ordinary clinical narrative must not be flagged as PHI."""
    from backend.app.privacy import is_safe
    assert is_safe(text), f"false positive on clean clinical text: {text!r}"


def test_privacy_address_and_mrn_are_actually_redacted():
    """Address/MRN patterns previously matched nothing; assert removal, not just detection."""
    from backend.app.privacy import redact_phi
    redacted, _ = redact_phi("Resides at 123 Main Street 45 with MRN A12345678")
    assert "123 Main Street 45" not in redacted
    assert "A12345678" not in redacted
