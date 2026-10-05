"""Core data models for the clinical intelligence system."""

from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import hashlib

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SafetySeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ConditionHypothesis(BaseModel):
    condition: str
    icd10_code: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_level: ConfidenceLevel
    supporting_factors: List[str] = Field(default_factory=list)
    against_factors: List[str] = Field(default_factory=list)
    recommended_workup: List[str] = Field(default_factory=list)


class SourceEvidence(BaseModel):
    source_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: str = ""
    year: Optional[int] = None
    pmid: Optional[str] = None
    excerpt: str = ""
    relevance_score: float = 0.0
    retrieval_attribution: float = 0.0
    dense_score: float = 0.0
    bm25_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0


class SafetyFlag(BaseModel):
    flag_type: str
    message: str
    severity: SafetySeverity


class XAIExplanation(BaseModel):
    retrieval_attribution: Dict[str, float] = Field(default_factory=dict)
    confidence_estimate: float = Field(ge=0.0, le=1.0)
    consistency_check: Optional[bool] = None
    counterfactual_explanation: Optional[Dict[str, Any]] = None
    faithfulness_score: Optional[float] = None
    claims: List[Dict[str, Any]] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)


class TrustMetrics(BaseModel):
    source_reliability: float = Field(ge=0.0, le=1.0)
    grounded_claim_rate: Optional[float] = None
    citation_validity: Optional[float] = None
    evidence_relevance: Optional[float] = None
    calibrated_confidence: Optional[float] = None
    abstain_status: Optional[bool] = None
    overall_label: Optional[str] = None
    checklist: Dict[str, Any] = Field(default_factory=dict)


class ClinicalCaseRequest(BaseModel):
    clinical_text: str = Field(..., min_length=10, max_length=5000)
    include_xai: bool = True
    include_trust: bool = True
    deep_mode: bool = False


class AnalysisResponse(BaseModel):
    case_id: str
    timestamp: str
    status: str = "completed"
    summary: str
    condition_hypotheses: List[ConditionHypothesis]
    differential_reasoning: str
    safety_flags: List[SafetyFlag] = Field(default_factory=list)
    evidence: List[SourceEvidence]
    retrieval_count: int
    confidence_overall: float
    confidence_level: ConfidenceLevel
    xai: Optional[XAIExplanation] = None
    trust_metrics: Optional[TrustMetrics] = None
    model_used: str
    provider: Optional[str] = None
    model_id_logged: Optional[str] = None
    processing_time_ms: int
    disclaimer: str = Field(
        default="RESEARCH USE ONLY. NOT FOR MEDICAL DECISION-MAKING. "
                "Consult a qualified clinician. This is a research tool, not a medical device."
    )
