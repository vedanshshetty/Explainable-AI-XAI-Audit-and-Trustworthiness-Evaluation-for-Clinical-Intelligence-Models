#!/usr/bin/env python3
"""System integration tests for clinical intelligence system."""

import sys
import os
import requests
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Change to project root so imports work
os.chdir(PROJECT_ROOT)


def test_privacy_module():
    """Test privacy redaction and detection."""
    print("\n=== Testing Privacy Module ===")

    from backend.app.privacy import redact_phi, detect_phi, is_safe

    test_cases = [
        ("Patient SSN: 123-45-6789", True, "SSN"),
        ("Phone: 555-123-4567", True, "phone"),
        ("DOB: 1990-01-15", True, "DOB"),
        ("Name: John Smith", True, "person_name"),
        ("Normal clinical text", False, None),
    ]

    all_passed = True
    for text, should_have_phi, expected_type in test_cases:
        redacted, found = redact_phi(text)
        safe = is_safe(text)

        has_phi = len(found) > 0
        if should_have_phi != has_phi:
            print(f"FAIL: {text}")
            print(f"  Expected PHI: {should_have_phi}, Got: {has_phi}")
            all_passed = False
        elif should_have_phi and expected_type not in found:
            print(f"FAIL: {text}")
            print(f"  Expected type {expected_type}, got: {found}")
            all_passed = False
        else:
            print(f"PASS: {text[:40]}... -> found={found}, safe={safe}")

    return all_passed


def test_rag_service():
    """Test RAG service components."""
    print("\n=== Testing RAG Service ===")

    from backend.app.rag_service import RAGService
    import asyncio

    service = RAGService()

    # Test initialization (async)
    try:
        asyncio.run(service.initialize())
        print("PASS: Service initialized")
    except Exception as e:
        print(f"FAIL: Service initialization: {e}")
        return False

    # Test corpus loading
    corpus = service._corpus
    if len(corpus) == 0:
        print("FAIL: Empty corpus")
        return False
    print(f"PASS: Corpus loaded ({len(corpus)} documents)")

    # Test BM25 retrieval
    if service.bm25 is None or not service.bm25._initialized:
        print("FAIL: BM25 index not built")
        return False
    results = service.bm25.search("myocardial infarction", k=3)
    if len(results) == 0:
        print("FAIL: BM25 returned no results")
        return False
    print(f"PASS: BM25 retrieval ({len(results)} results)")

    # Test FAISS retrieval
    if service.faiss is None or not service.faiss._initialized:
        print("FAIL: FAISS index not built")
        return False
    print(f"PASS: FAISS index built (dimension: {service.faiss.dim}, docs: {service.faiss.ntotal})")

    return True


def test_backend_api():
    """Test backend API endpoints."""
    print("\n=== Testing Backend API ===")

    # Test root endpoint
    r = requests.get("http://localhost:8000/", timeout=5)
    if r.status_code != 200:
        print(f"FAIL: Root endpoint returned {r.status_code}")
        return False
    data = r.json()
    if data.get("status") != "operational":
        print(f"FAIL: Unexpected status: {data}")
        return False
    print("PASS: Root endpoint")

    # Test status endpoint
    r = requests.get("http://localhost:8000/api/v1/status", timeout=5)
    if r.status_code != 200:
        print(f"FAIL: Status endpoint returned {r.status_code}")
        return False
    data = r.json()
    if "model" not in data or "k_retrieve" not in data:
        print(f"FAIL: Missing fields in status response")
        return False
    print(f"PASS: Status endpoint (model={data['model']})")

    # Test analyze endpoint
    payload = {
        "clinical_text": "55-year-old male presents with chest pain radiating to left arm. History of hypertension and diabetes. ECG shows ST elevation.",
        "include_xai": True,
        "include_trust": True,
        "deep_mode": False,
    }
    r = requests.post("http://localhost:8000/api/v1/analyze", json=payload, timeout=180)
    if r.status_code != 200:
        print(f"FAIL: Analyze endpoint returned {r.status_code}: {r.text}")
        return False
    data = r.json()
    required_fields = ["condition_hypotheses", "safety_flags", "confidence_overall"]
    for field in required_fields:
        if field not in data:
            print(f"FAIL: Missing field '{field}' in response")
            return False
    print(
        f"PASS: Analyze endpoint (conditions={len(data['condition_hypotheses'])}, confidence={data['confidence_overall']:.2f})"
    )

    return True


def test_unit_tests():
    """Run unit tests."""
    print("\n=== Running Unit Tests ===")
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_clinical_system.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Count passed tests
        lines = result.stdout.split("\n")
        for line in lines:
            if "passed" in line and "in" in line:
                print(f"PASS: {line.strip()}")
                return True
        print("PASS: All tests passed")
        return True
    else:
        print(f"FAIL: Tests failed\n{result.stdout[-500:]}")
        return False


def main():
    """Run all system tests."""
    print("=" * 60)
    print("Clinical Intelligence System - Integration Tests")
    print("=" * 60)

    results = {
        "Privacy Module": test_privacy_module(),
        "RAG Service": test_rag_service(),
        "Backend API": test_backend_api(),
        "Unit Tests": test_unit_tests(),
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:20s}: {status}")

    all_passed = all(results.values())
    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
