"""Frontend for clinical intelligence system with Streamlit."""

import json
import time
from urllib.parse import urlparse

import requests
import streamlit as st

st.set_page_config(page_title="Clinical Intelligence System", page_icon="hospital", layout="wide")

API_URL = "http://localhost:8000"

# Demo cases for recorded video
DEMO_CASES = {
    "Select a case...": "",
    "Typical pneumonia case": "65-year-old male presents with 3-day history of fever, productive cough with purulent sputum, pleuritic chest pain, and shortness of breath. Temperature 38.9C, HR 110, BP 128/78, RR 22, SpO2 92% on room air. Lung exam reveals decreased breath sounds and crackles at right lower lobe.",
    "Acute stroke vignette": "72-year-old female presents with sudden onset of right-sided facial droop, right arm weakness, and slurred speech. Last known well 2 hours ago. Past medical history significant for atrial fibrillation on warfarin. NIHSS score estimated at 15.",
    "MI presentation": "58-year-old male with history of hypertension and diabetes presents with 2 hours of substernal chest pressure radiating to left arm, associated with diaphoresis and nausea. ECG shows ST elevation in leads II, III, aVF.",
    "Abstention case (gibberish)": "xkcd qmzj plrt bvxw tnfh gkyc zjqp wrmx lbvn dsht yfcg pqwr zlmn.",
    "Sepsis case": "68-year-old male with recent urinary tract infection presents with fever 39.2C, confusion, HR 120, BP 88/50, RR 28. WBC 18000 with left shift. Lactate 4.2.",
}

# â”€â”€ Consent gate â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "consented" not in st.session_state:
    st.session_state["consented"] = False

if not st.session_state["consented"]:
    st.markdown("## Clinical Intelligence System - Research Tool")
    st.markdown("""
    ### Consent Required
    
    This is a **research tool only**, not for clinical use.
    
    By proceeding, you acknowledge that:
    - Your input text will be sent to a **third-party cloud LLM** (OpenRouter) for processing.
    - Text may be processed by models hosted outside your country.
    - No PHI should be entered; this is a demo with synthetic data only.
    - Results are **not diagnostic** and must not be used for clinical decisions.
    
    [ ] I consent to send my clinical text to a third-party cloud model for analysis.
    """)
    if st.button("I Consent and Proceed", type="primary", key="consent_btn"):
        st.session_state["consented"] = True
        st.rerun()
    st.stop()

# â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.header("Settings")
    deep_mode = st.checkbox("Deep XAI mode (slower, more detailed)", value=False)
    include_xai = st.checkbox("Include XAI explanations", value=True)
    include_trust = st.checkbox("Include trust metrics", value=True)
    st.markdown("---")
    st.markdown("### Demo Cases")
    selected_case = st.selectbox("", list(DEMO_CASES.keys()))
    if st.button("Load Demo Case"):
        st.session_state["last_case"] = DEMO_CASES[selected_case]

st.title("Clinical Intelligence System")
st.markdown("Research-focused clinical decision support with XAI and trust evaluation")
st.markdown("> **Disclaimer:** This is a research tool. Not for medical decision-making. Consult a qualified clinician.")

# â”€â”€ Input â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.subheader("Enter Clinical Case")
clinical_text = st.text_area(
    "Clinical case description:",
    height=200,
    placeholder="Describe the patient's presentation, vital signs, exam findings, and key history..."
)

if st.button("Analyze Case", type="primary"):
    if not clinical_text.strip():
        st.warning("Please enter a clinical case description.")
    else:
        with st.spinner("Analyzing case..."):
            try:
                start_time = time.time()
                payload = {
                    "clinical_text": clinical_text,
                    "include_xai": include_xai,
                    "include_trust": include_trust,
                    "deep_mode": deep_mode,
                }
                
                resp = requests.post(f"{API_URL}/api/v1/analyze", json=payload, timeout=180)
                elapsed_ms = int((time.time() - start_time) * 1000)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Summary
                    st.subheader("Analysis Results")
                    if data.get("summary"):
                        st.info(data["summary"])
                    
                    # Safety flags
                    if data.get("safety_flags"):
                        st.subheader("Safety Flags")
                        for flag in data["safety_flags"]:
                            severity = flag.get("severity", "info")
                            icon = {"critical": "ðŸ”´", "warning": "ðŸŸ¡", "info": "ðŸ”µ"}.get(severity, "âšª")
                            st.markdown(f"{icon} **{flag.get('flag_type', 'Flag')}**: {flag.get('message', '')}")
                    
                    # Condition hypotheses
                    if data.get("condition_hypotheses"):
                        st.subheader("Condition Hypotheses")
                        for i, cond in enumerate(data["condition_hypotheses"], 1):
                            with st.expander(f"{i}. {cond.get('condition', 'Condition')} (Confidence: {cond.get('confidence', 0):.0%})"):
                                st.markdown(f"**Supporting Factors:**")
                                for f in cond.get("supporting_factors", []):
                                    st.markdown(f"- {f}")
                                if cond.get("against_factors"):
                                    st.markdown(f"**Against Factors:**")
                                    for f in cond.get("against_factors", []):
                                        st.markdown(f"- {f}")
                    
                    # Source evidence
                    if data.get("source_evidence"):
                        st.subheader("Source Evidence")
                        for ev in data["source_evidence"][:5]:
                            with st.expander(f"{ev.get('title', 'Source')} ({ev.get('journal', '')}, {ev.get('year', '')})"):
                                st.markdown(f"**PMID:** {ev.get('pmid', 'N/A')}")
                                st.markdown(f"**Authors:** {', '.join(ev.get('authors', []))}")
                                st.markdown(f"**Abstract:** {ev.get('excerpt', '')[:500]}...")
                                scores = {}
                                if ev.get("dense_score"): 
                                    scores["Dense"] = round(ev["dense_score"], 3)
                                if ev.get("bm25_score"): 
                                    scores["BM25"] = round(ev["bm25_score"], 3)
                                if ev.get("rrf_score"): 
                                    scores["RRF"] = round(ev["rrf_score"], 3)
                                if ev.get("rerank_score"): 
                                    scores["Rerank"] = round(ev["rerank_score"], 3)
                                if scores:
                                    st.json(scores)
                    
                    # Differential reasoning
                    if data.get("differential_reasoning"):
                        st.subheader("Differential Reasoning")
                        st.markdown(data["differential_reasoning"])
                    
                    # XAI
                    if include_xai and data.get("xai"):
                        xai = data["xai"]
                        st.subheader("Explainable AI (XAI)")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Confidence Estimate", f"{xai.get('confidence_estimate', 0):.0%}")
                        with col2:
                            st.metric("Consistency Check", "Pass" if xai.get('consistency_check') else "Fail")
                        with col3:
                            st.metric("Faithfulness", f"{xai.get('faithfulness_score', 0):.2f}" if xai.get('faithfulness_score') else "N/A")
                    
                    # Trust
                    if include_trust and data.get("trust_metrics"):
                        trust = data["trust_metrics"]
                        st.subheader("Trust Evaluation")
                        checklist = trust.get("checklist", {})
                        for key, val in checklist.items():
                            if val is not None:
                                st.markdown(f"- **{key.replace('_', ' ').title()}**: {val}")
                        st.markdown(f"**Overall Label**: {trust.get('overall_label', 'N/A')}")
                    
                    # Model info
                    st.caption(f"Model: {data.get('model_used', 'unknown')} | Provider: {data.get('provider', 'unknown')} | Time: {elapsed_ms}ms")
                    
                    # Disclaimer
                    st.warning(data.get("disclaimer", "RESEARCH USE ONLY."))
                    
                else:
                    st.error(f"Error {resp.status_code}: {resp.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"Cannot connect to API at {API_URL}. Is the backend running?")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

# â”€â”€ Ethics Results Page â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.expander("Ethics Evaluation Results"):
    import os
    results_dir = "evaluation/results"
    if os.path.exists(results_dir):
        for fname in sorted(os.listdir(results_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(results_dir, fname)
                with open(fpath, "r") as f:
                    try:
                        result = json.load(f)
                        st.subheader(fname)
                        st.json(result)
                    except:
                        pass
    else:
        st.info("No evaluation results yet. Run the ethics study first.")