/** Response shapes returned by POST /api/v1/analyze on the FastAPI backend. */

export type ConfidenceLevel = "high" | "medium" | "low";
export type SafetySeverity = "info" | "warning" | "critical";

export interface SafetyFlag {
  flag_type: string;
  message: string;
  severity: SafetySeverity;
}

export interface ConditionHypothesis {
  condition: string;
  icd10_code: string | null;
  confidence: number;
  confidence_level: ConfidenceLevel;
  supporting_factors: string[];
  against_factors: string[];
  recommended_workup: string[];
  /** 1-based indices into `evidence`, produced by resolving [Source N] markers. */
  source_refs: number[];
}

export interface SourceEvidence {
  source_id: string;
  title: string;
  authors: string[];
  journal: string;
  year: number | null;
  pmid: string | null;
  /** Present only for records that genuinely came from PubMed. */
  pmid_url: string | null;
  excerpt: string;
  relevance_score: number;
  /** Logistic-normalised rerank score, 0..1, for charting. */
  relevance_normalized: number;
  attribution_score: number;
  citation_index: number;
  cited: boolean;
  cited_by: string[];
  retrieval_attribution: number;
  dense_score: number;
  bm25_score: number;
  rrf_score: number;
  rerank_score: number;
}

export interface XaiExplanation {
  retrieval_attribution: Record<string, number>;
  confidence_estimate: number;
  consistency_check: boolean | null;
  counterfactual_explanation: {
    removed_source?: string;
    source_weight?: number;
    confidence_before?: number;
    confidence_without_source?: number;
    confidence_delta?: number;
    verdict?: string;
  } | null;
  faithfulness_score: number | null;
  claims: Array<{
    claim: string;
    hypothesis: string | null;
    sources: number[];
    grounding: number;
  }>;
  unsupported_claims: string[];
}

export interface TrustMetrics {
  source_reliability: number;
  grounded_claim_rate: number | null;
  citation_validity: number | null;
  evidence_relevance: number | null;
  calibrated_confidence: number | null;
  abstain_status: boolean | null;
  overall_label: string | null;
  overall_trust_score: number;
  checklist: Record<string, number | boolean>;
}

export interface AnalysisResponse {
  case_id: string;
  timestamp: string;
  status: string;
  summary: string;
  condition_hypotheses: ConditionHypothesis[];
  differential_reasoning: string;
  safety_flags: SafetyFlag[];
  evidence: SourceEvidence[];
  retrieval_count: number;
  confidence_overall: number;
  confidence_level: ConfidenceLevel;
  xai: XaiExplanation | null;
  trust_metrics: TrustMetrics | null;
  model_used: string;
  provider: string | null;
  model_id_logged: string | null;
  processing_time_ms: number;
  citations_used: number;
  citation_validity: number;
  citation_coverage: number;
  disclaimer: string;
}

export interface AnalyzeRequest {
  clinical_text: string;
  include_xai: boolean;
  include_trust: boolean;
  deep_mode: boolean;
}

export interface SampleCase {
  id: string;
  label: string;
  focus: string;
  text: string;
}

export type ViewKey = "analysis" | "cases" | "xai" | "trust";

export const SAMPLE_CASES: SampleCase[] = [
  {
    id: "pneumonia",
    label: "Community-acquired pneumonia",
    focus: "Respiratory · infectious",
    text:
      "65-year-old male presents with a 3-day history of fever, productive cough with purulent " +
      "sputum, pleuritic chest pain, and shortness of breath. Temperature 38.9 C, HR 110, " +
      "BP 128/78, RR 22, SpO2 92% on room air. Lung exam reveals decreased breath sounds and " +
      "crackles at the right lower lobe.",
  },
  {
    id: "stroke",
    label: "Acute ischemic stroke",
    focus: "Neurological · time-critical",
    text:
      "72-year-old female presents with sudden onset of right-sided facial droop, right arm " +
      "weakness, and slurred speech. Last known well 2 hours ago. Past medical history " +
      "significant for atrial fibrillation on warfarin. NIHSS score estimated at 15.",
  },
  {
    id: "mi",
    label: "Acute myocardial infarction",
    focus: "Cardiac · emergency",
    text:
      "58-year-old male with history of hypertension and diabetes presents with 2 hours of " +
      "substernal chest pressure radiating to the left arm, associated with diaphoresis and " +
      "nausea. ECG shows ST elevation in leads II, III, and aVF.",
  },
  {
    id: "sepsis",
    label: "Sepsis with organ dysfunction",
    focus: "Systemic · critical care",
    text:
      "68-year-old male with a recent urinary tract infection presents with fever 39.2 C, new " +
      "confusion, HR 120, BP 88/50, RR 28. WBC 18000 with left shift. Lactate 4.2 mmol/L.",
  },
  {
    id: "insufficient",
    label: "Insufficient information",
    focus: "Abstention test",
    text: "Patient reports feeling unwell. Staff observed the patient during the visit.",
  },
];