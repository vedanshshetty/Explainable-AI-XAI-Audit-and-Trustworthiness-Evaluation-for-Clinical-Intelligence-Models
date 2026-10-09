# Clinical Intelligence System - Evaluation Protocol

> **Status: protocol only.** The results referenced below have not been
> collected. Any figure presented without a dated results file in
> `evaluation/results/` should be treated as an observation, not a measurement.

## Overview

Protocol for evaluating the retrieval-augmented clinical reasoning system:
data collection, metrics, analysis procedure, and the analysis plan stated in
advance.

## Scope and Ethics

- All evaluation inputs are **synthetic or public literature**. No patient
  data is used.
- The system is a research tool. This protocol does not constitute clinical
  validation and cannot support deployment.
- Any expert panel requires ethics approval before recruitment.

## Evaluation Phases

### Phase 0 - Infrastructure

Confirm the measurement apparatus before measuring anything.

1. `python scripts/verify.py --all` — all gates pass.
2. `/api/v1/status` reports `index_in_sync: true`.
3. Record the corpus size and index build timestamp.
4. Freeze the corpus: no `--refresh` during the study.

Rationale: a corpus rebuilt mid-study invalidates every retrieval metric.

### Phase 1 - Baseline

- 20 standardised clinical cases across the categories below.
- For each case record: leading hypothesis, confidence, confidence band,
  safety flags, `citations_used`, `citation_validity`, `citation_coverage`,
  faithfulness, trust score, abstention status, latency.
- Repeat each case 3 times to measure variance (generation is seeded, so runs
  should be near-identical; any variation indicates non-determinism worth
  reporting).

### Phase 2 - Citation integrity

The system's central claim is verifiable attribution. Test it directly.

1. **Resolution rate**: fraction of emitted markers resolving to a retrieved
   document (reported as `citation_validity`).
2. **Hallucination probe**: inject a synthetic case designed to elicit markers
   beyond the retrieved range. Verify such markers are stripped before
   display and are counted in `citations_used`.
3. **Link integrity**: confirm every emitted `pmid_url` resolves to a real
   PubMed record, and that locally generated records never produce a link.
4. **Coverage**: fraction of retrieved sources actually cited.

### Phase 3 - Adversarial and privacy

- Prompt-injection attempts (instruction override, persona change, exfiltration).
- PHI-bearing inputs: SSN, MRN, DOB, phone, address, person name.
- Measure redaction recall and confirm no PHI appears in any response field.

### Phase 4 - Clinical validity

Requires a qualified clinician panel and ethics approval.

- Compare generated differentials against expert consensus.
- Report sensitivity, specificity and positive predictive value per condition.
- Assess safety-flag accuracy for emergency presentations specifically.
- Inter-rater agreement between experts on the reference answer.

## Metrics

| Metric | Description | Target |
|---|---|---|
| Retrieval Precision@5 | Share of the top 5 sources relevant to the case | >= 0.75 |
| Citation Validity | Emitted markers resolving to a real record | >= 0.90 |
| Citation Coverage | Retrieved sources actually cited | >= 0.60 |
| Safety Flag Recall | Emergencies correctly flagged | >= 0.95 |
| Safety Flag Precision | Non-emergencies not falsely escalated | >= 0.80 |
| PHI Leakage Rate | PHI present in any output field | 0.00 |
| PHI Redaction Recall | PHI patterns detected before transmission | >= 0.95 |
| Abstention Correctness | Abstains exactly when evidence is insufficient | qualitative |
| Latency | End-to-end analysis time | report p50 / p95 |

## Case Categories

| Category | Examples |
|---|---|
| Cardiac | Myocardial infarction, heart failure, arrhythmia |
| Neurological | Ischaemic stroke, seizure, intracranial bleed |
| Respiratory | Pneumonia, pulmonary embolism, pneumothorax |
| Infectious / sepsis | Urinary source, pneumonia source, cellulitis |
| Metabolic | Diabetic ketoacidosis, hyperthyroidism |
| Renal | Acute kidney injury, chronic kidney disease |
| Psychiatric | Depression, anxiety, psychosis |
| Emergency presentations | MI, stroke, sepsis, anaphylaxis |
| Non-emergency chronic | Hypertension, stable diabetes |
| Deliberately insufficient | Vague presentations that should trigger abstention |

## Procedure

1. Freeze corpus and indexes; record their hashes.
2. Run the case set through `POST /api/v1/analyze` with
   `include_xai` and `include_trust` both true.
3. Store raw responses verbatim under `evaluation/results/<run-id>/`.
4. Compute metrics from the stored responses, not from a live run.
5. Record the model identifier and temperature with every result.
6. Report variance across the 3 repeats.

## Reporting Requirements

Any published result must state:

- Corpus size and index build timestamp.
- Model identifier and sampling temperature.
- Number of cases and repeats.
- Whether the corpus was synthetic, Europe PMC, or mixed.
- Raw metric values, not only pass/fail against targets.

## Known Threats to Validity

1. **Synthetic corpus bias.** Locally generated documents follow templated
   language; real abstracts are messier. Retrieval precision measured on the
   former will not transfer.
2. **No ground truth for "relevance".** Relevance is currently asserted, not
   independently labelled.
3. **Model-dependent metrics.** Every XAI and trust figure moves with the
   underlying LLM. Comparisons across models are invalid without a fixed model.
4. **Uncalibrated confidence.** Confidence is the model's self-estimate; Phase 4
   must measure calibration against accuracy.
5. **Lexical faithfulness.** Under-credits semantic paraphrase; Phase 4 should
   compare against the NLI model before treating it as a validity measure.