"""PHI redaction for clinical text input."""

import re
from typing import List, Tuple, Dict


PHI_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b', re.IGNORECASE), 'SSN'),
    (re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', re.IGNORECASE), 'phone'),
    (re.compile(r'\+\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}', re.IGNORECASE), 'phone_intl'),
    (re.compile(r'\b\d{4}[/\-]\d{2}[/\-]\d{2}\b', re.IGNORECASE), 'DOB'),
    (re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE), 'DOB_written'),
    (re.compile(r'\b\d+\\s+[A-Z][a-z]+\\s+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|Lane|Ln|Court|Ct|Way|Place|Pl)\\.?\\s+\d+', re.IGNORECASE), 'address'),
    (re.compile(r'\b(?:MRN|medical record number|Patient ID|patient_id)\\s*[:#\\-]?\\s*[A-Z0-9\\-]{4,20}\\b', re.IGNORECASE), 'medical_record_number'),
    (re.compile(r'\bID[:\\#]\\s*[A-Z0-9\\-]{3,30}\\b', re.IGNORECASE), 'patient_identifier'),
    (re.compile(r'\bA\d{7}\b', re.IGNORECASE), 'MRN_alphanumeric'),
    (re.compile(r'\b(?:John|Smith|Jane|Doe|Robert|Michael|Emily|Sarah|David|Lisa)\b', re.IGNORECASE), 'person_name'),
]

PHI_REPLACEMENT = '[REDACTED]'


def redact_phi(text: str) -> Tuple[str, List[str]]:
    """Replace known PHI patterns with [REDACTED]. Returns (redacted_text, list_of_found_types)."""
    found: List[str] = []
    for pattern, label in PHI_PATTERNS:
        if pattern.search(text):
            found.append(label)
        text = pattern.sub(PHI_REPLACEMENT, text)
    return text, found


def detect_phi(text: str) -> List[str]:
    """Return list of PHI types found in text."""
    found: List[str] = []
    for pattern, label in PHI_PATTERNS:
        if pattern.search(text):
            found.append(label)
    return found


def is_safe(text: str) -> bool:
    """Return True if no PHI detected."""
    return len(detect_phi(text)) == 0


def redaction_preview(text: str) -> Dict[str, Any]:
    """Return preview of what would be redacted."""
    redacted, found = redact_phi(text)
    return {
        "original_length": len(text),
        "redacted_length": len(redacted),
        "phi_types_found": found,
        "redacted_text": redacted,
        "is_safe": len(found) == 0
    }


def get_redacted(text: str) -> str:
    """Return redacted text for outbound requests."""
    redacted, _ = redact_phi(text)
    return redacted


def count_redactions(original: str, redacted: str) -> int:
    """Count number of redaction replacements."""
    return original.count('[REDACTED]') != redacted.count('[REDACTED]') and 1 or redacted.count(PHI_REPLACEMENT)
