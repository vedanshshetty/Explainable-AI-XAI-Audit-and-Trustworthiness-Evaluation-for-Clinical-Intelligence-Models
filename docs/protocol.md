# Clinical Intelligence System - Evaluation Protocol

## Overview

This document outlines the protocol for evaluating the clinical intelligence system, including data collection, evaluation metrics, and analysis procedures.

## Evaluation Phases

### Phase 1: Baseline Testing
- Run the RAG pipeline on a set of 20 standardized clinical cases
- Measure retrieval accuracy, hypothesis quality, and safety flag generation
- Record confidence scores and trust metrics for each case

### Phase 2: Adversarial Testing
- Test with injection attempts and PHI-containing inputs
- Verify privacy redaction and injection guard functionality
- Measure robustness against prompt injection attacks

### Phase 3: Clinical Validity
- Compare generated differential diagnoses against expert consensus
- Measure sensitivity, specificity, and positive predictive value
- Assess safety flag accuracy for emergency presentations

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Retrieval Precision@5 | Top-5 retrieval accuracy | >= 0.75 |
| Hypothesis Validity | % of hypotheses clinically valid | >= 0.80 |
| Safety Flag Recall | % of emergencies correctly flagged | >= 0.95 |
| PHI Leakage Rate | % of PHI detected in outputs | <= 0.05 |
| Trust Score Accuracy | Correlation with expert assessment | >= 0.60 |

## Case Categories
- Cardiac (MI, heart failure)
- Neurological (stroke, seizure)
- Infectious (sepsis, pneumonia)
- Metabolic (DKA, hyperthyroidism)
- Psychiatric (depression, anxiety)
- Emergency presentations
- Non-emergency chronic conditions
