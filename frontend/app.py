"""Clinical Intelligence System - frontend.

Dark clinical research interface. Streamlit's chrome is removed and the layout
is rebuilt with a small stylesheet: one accent colour, hairline borders, flat
panels, tight vertical rhythm.

Results are presented with inline SVG charts (no plotting dependency) so the
whole surface can be styled to match the panels.

Pure Streamlit.
"""

import os
import threading
import time

import requests
import streamlit as st

st.set_page_config(page_title="Clinical Intelligence System", page_icon=None,
                   layout="wide", initial_sidebar_state="expanded")


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:#080B12; --panel:#0F141D; --panel-2:#141A26;
    --line:rgba(255,255,255,0.08); --line-2:rgba(255,255,255,0.15);
    --text:#E4E9F2; --muted:#98A3B3; --faint:#6B7688;
    --teal:#2DD4BF; --cyan:#38BDF8; --amber:#E0A64B; --red:#E57272;
}

html, body, [class*="css"] {
    font-family:'Inter', -apple-system, 'Segoe UI', sans-serif;
    color:var(--text); -webkit-font-smoothing:antialiased;
}

/* Remove Streamlit chrome. */
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stStatusWidget"],
[data-testid="stDecoration"], [data-testid="stToolbar"], [data-testid="stToolbarActions"],
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"], [data-testid="stExpandSidebarButtonContainer"],
[data-testid="stWidgetLabel"] { display:none !important; }
header[data-testid="stHeader"] { background:transparent; height:0; min-height:0; overflow:hidden; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:var(--bg); }

/* Tight vertical rhythm: remove Streamlit's default block gap. */
.block-container { padding:1rem 2rem 2.5rem !important; max-width:1240px !important; }
[data-testid="stVerticalBlock"], [data-testid="stVerticalBlockBorderWrapper"] { gap:0 !important; }
[data-testid="stHorizontalBlock"] { gap:0.6rem !important; }
[data-testid="stElementContainer"], [data-testid="stSpacer"] { min-height:0 !important; }
hr { border-color:var(--line); margin:0.9rem 0; }
::selection { background:rgba(45,212,191,0.25); }
::-webkit-scrollbar { width:9px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.10); border-radius:9px; }

/* ── Header ─────────────────────────────────────────────────────────────── */
.top { display:flex; align-items:center; gap:0.75rem; padding-bottom:0.85rem; margin-bottom:1rem;
       border-bottom:1px solid var(--line); }
.top h1 { font-size:1.08rem; font-weight:600; letter-spacing:-0.014em; color:#fff; margin:0; }
.top p { font-size:0.8rem; color:var(--muted); margin:0.1rem 0 0; }
.top .note { margin-left:auto; white-space:nowrap; font-size:0.66rem; font-weight:500;
    letter-spacing:0.07em; text-transform:uppercase; color:#E7C288;
    background:rgba(224,166,75,0.10); border:1px solid rgba(224,166,75,0.30);
    border-radius:5px; padding:0.2rem 0.5rem; }

/* ── Sections ───────────────────────────────────────────────────────────── */
.sec { display:flex; align-items:baseline; gap:0.6rem; margin:1.1rem 0 0.5rem; }
.sec.first { margin-top:0.2rem; }
.sec h2 { font-size:0.7rem; font-weight:600; letter-spacing:0.11em; text-transform:uppercase;
         color:var(--muted); margin:0; white-space:nowrap; }
.sec .line { flex:1; height:1px; background:var(--line); }
.sec .n { font-size:0.7rem; color:var(--faint); font-family:'JetBrains Mono',monospace; }

/* ── Card ───────────────────────────────────────────────────────────────── */
.card { background:var(--panel); border:1px solid var(--line); border-radius:10px;
        padding:0.85rem 0.95rem; margin-bottom:0.45rem; }
.card .head { font-size:0.9rem; font-weight:600; color:#fff; margin-bottom:0.4rem; }
.card .sub2 { font-size:0.76rem; color:var(--faint); margin:-0.25rem 0 0.55rem; }
.body { font-size:0.885rem; line-height:1.68; color:#D2D9E5; }
.small { font-size:0.79rem; color:var(--muted); line-height:1.6; }

/* ── Charts ─────────────────────────────────────────────────────────────── */
.chart { width:100%; display:block; overflow:visible; }
.axis { font-family:'JetBrains Mono',monospace; font-size:9px; fill:var(--faint); }
.grid-line { stroke:rgba(255,255,255,0.055); stroke-width:1; }
.barrow { display:flex; align-items:center; gap:0.5rem; margin-bottom:0.32rem; }
.barrow .lb { flex:0 0 92px; font-size:0.76rem; color:var(--muted);
              overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.barrow .track { flex:1; height:7px; border-radius:4px; background:rgba(255,255,255,0.07); overflow:hidden; }
.barrow .fill { height:100%; border-radius:4px; }
.barrow .val { flex:0 0 40px; text-align:right; font-family:'JetBrains Mono',monospace;
               font-size:0.74rem; color:var(--text); }
.legend { display:flex; gap:0.9rem; flex-wrap:wrap; margin-top:0.5rem; font-size:0.73rem; color:var(--muted); }
.legend i { display:inline-block; width:7px; height:7px; border-radius:2px; margin-right:0.3rem; }

/* ── Stats ──────────────────────────────────────────────────────────────── */
.stats { display:flex; gap:1.9rem; flex-wrap:wrap; margin-top:0.7rem; }
.stat .k { font-size:0.66rem; font-weight:500; letter-spacing:0.08em; text-transform:uppercase;
           color:var(--faint); margin-bottom:0.14rem; }
.stat .v { font-size:1.28rem; font-weight:600; letter-spacing:-0.02em; color:#fff; }
.stat .d { font-size:0.73rem; color:var(--muted); }

/* ── Meter ──────────────────────────────────────────────────────────────── */
.meter { height:4px; border-radius:4px; background:rgba(255,255,255,0.08); overflow:hidden; }
.meter i { display:block; height:100%; border-radius:4px; }

/* ── Safety flag ────────────────────────────────────────────────────────── */
.flag { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--faint);
        border-radius:9px; padding:0.65rem 0.8rem; margin-bottom:0.35rem; }
.flag .t { font-size:0.83rem; font-weight:600; color:#fff; margin-bottom:0.08rem; }
.flag .m { font-size:0.845rem; line-height:1.5; color:#C7D0DD; }
.flag.critical { border-left-color:var(--red); }
.flag.warning { border-left-color:var(--amber); }
.flag.info { border-left-color:var(--cyan); }

/* ── Hypothesis ─────────────────────────────────────────────────────────── */
.hyp { background:var(--panel); border:1px solid var(--line); border-left:3px solid var(--teal);
       border-radius:10px; padding:0.8rem 0.9rem; margin-bottom:0.4rem; }
.hyp .line1 { display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; }
.hyp .nm { font-size:0.93rem; font-weight:600; color:#fff; }
.tag { font-size:0.63rem; font-weight:600; letter-spacing:0.07em; text-transform:uppercase;
       padding:0.13rem 0.44rem; border-radius:4px; white-space:nowrap; margin-left:auto; }
.tag.high { color:var(--teal); background:rgba(45,212,191,0.13); border:1px solid rgba(45,212,191,0.30); }
.tag.medium { color:var(--amber); background:rgba(224,166,75,0.13); border:1px solid rgba(224,166,75,0.30); }
.tag.low { color:var(--red); background:rgba(229,114,114,0.13); border:1px solid rgba(229,114,114,0.30); }
.sub { font-size:0.65rem; font-weight:600; letter-spacing:0.10em; text-transform:uppercase;
       color:var(--faint); margin:0.7rem 0 0.28rem; }
.fx { list-style:none; padding:0; margin:0; }
.fx li { font-size:0.85rem; line-height:1.5; color:#C7D0DD; padding:0.13rem 0 0.13rem 0.9rem; position:relative; }
.fx li::before { content:''; position:absolute; left:0.1rem; top:0.58rem;
                 width:4px; height:4px; border-radius:4px; background:var(--teal); }
.fx.against li::before { background:var(--red); }
.fx.workup li::before { background:var(--cyan); }
.refs { display:flex; flex-wrap:wrap; gap:0.22rem; margin-top:0.55rem; }
.ref { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--teal);
       background:rgba(45,212,191,0.10); border:1px solid rgba(45,212,191,0.25);
       border-radius:4px; padding:0.06rem 0.32rem; }

/* ── Key / value ────────────────────────────────────────────────────────── */
.kv { display:flex; align-items:center; justify-content:space-between; gap:1rem;
      font-size:0.83rem; padding:0.34rem 0; border-bottom:1px solid var(--line); }
.kv:last-child { border-bottom:none; }
.kv .k { color:var(--muted); }
.kv .v { font-family:'JetBrains Mono',monospace; font-size:0.79rem; color:var(--text); }
.kv .v.ok { color:var(--teal); } .kv .v.warn { color:var(--amber); } .kv .v.bad { color:var(--red); }

/* ── Sidebar ────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] { background:#0B0F17; border-right:1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { font-size:0.79rem; color:var(--muted); line-height:1.55; }
[data-testid="stSidebar"] .stCheckbox label { font-size:0.83rem; }
.side-h { font-size:0.66rem; font-weight:600; letter-spacing:0.11em; text-transform:uppercase;
          color:var(--faint); margin:0 0 0.45rem; }

/* ── Controls ───────────────────────────────────────────────────────────── */
.stButton > button, .stLinkButton > a {
    width:100%; border-radius:7px !important; padding:0.42rem 0.7rem;
    font-family:'Inter',sans-serif; font-size:0.83rem; font-weight:500;
    color:var(--text) !important; background:var(--panel) !important;
    border:1px solid var(--line) !important;
    transition:border-color .14s ease, background .14s ease;
}
.stButton > button:hover, .stLinkButton > a:hover {
    background:var(--panel-2) !important; border-color:var(--line-2) !important; color:#fff !important; }
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
    background:var(--teal) !important; border:1px solid var(--teal) !important;
    color:#06231F !important; font-size:0.89rem; font-weight:600; padding:0.55rem 1rem; }
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background:#3FE0CB !important; color:#06231F !important; }
[data-testid="stSidebar"] .stButton > button {
    justify-content:flex-start; text-align:left; font-size:0.81rem;
    background:transparent !important; border-color:transparent !important; padding:0.38rem 0.6rem; }
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(255,255,255,0.045) !important; border-color:var(--line) !important; }
.stTextAreaRoot textarea, .stTextInputRoot input {
    background:var(--panel) !important; border:1px solid var(--line) !important;
    border-radius:9px !important; color:var(--text) !important;
    font-family:'Inter',sans-serif !important; font-size:0.9rem !important;
    line-height:1.65 !important; padding:0.7rem 0.8rem !important; box-shadow:none !important; }
.stTextAreaRoot textarea:focus, .stTextInputRoot input:focus {
    outline:none !important; border-color:rgba(45,212,191,0.45) !important; }
.stTextAreaRoot textarea::placeholder { color:var(--faint) !important; }
.stCaption, [data-testid="stCaptionContainer"] { color:var(--faint) !important; font-size:0.77rem !important; }
.stAlert { border-radius:9px !important; border:1px solid var(--line) !important;
           background:var(--panel) !important; font-size:0.85rem; }
details[data-testid="stExpander"] {
    background:var(--panel); border:1px solid var(--line); border-radius:9px; margin-bottom:0.35rem; }
details[data-testid="stExpander"] summary { font-size:0.845rem; font-weight:500; color:var(--text); }
details[data-testid="stExpander"] summary:hover { color:var(--teal); }
</style>
"""


TEAL, CYAN, AMBER, RED = "#2DD4BF", "#38BDF8", "#E0A64B", "#E57272"

CASES = {
    "Community-acquired pneumonia": (
        "65-year-old male presents with a 3-day history of fever, productive cough with purulent "
        "sputum, pleuritic chest pain, and shortness of breath. Temperature 38.9 C, HR 110, "
        "BP 128/78, RR 22, SpO2 92% on room air. Lung exam reveals decreased breath sounds and "
        "crackles at the right lower lobe."
    ),
    "Acute ischemic stroke": (
        "72-year-old female presents with sudden onset of right-sided facial droop, right arm "
        "weakness, and slurred speech. Last known well 2 hours ago. Past medical history "
        "significant for atrial fibrillation on warfarin. NIHSS score estimated at 15."
    ),
    "Acute myocardial infarction": (
        "58-year-old male with history of hypertension and diabetes presents with 2 hours of "
        "substernal chest pressure radiating to the left arm, associated with diaphoresis and "
        "nausea. ECG shows ST elevation in leads II, III, and aVF."
    ),
    "Sepsis with organ dysfunction": (
        "68-year-old male with a recent urinary tract infection presents with fever 39.2 C, new "
        "confusion, HR 120, BP 88/50, RR 28. WBC 18000 with left shift. Lactate 4.2 mmol/L."
    ),
    "Insufficient information": (
        "Patient reports feeling unwell. Staff observed the patient during the visit."
    ),
}

DISCLAIMER = (
    "Research use only. Not a medical device and not for clinical decision-making. "
    "Outputs are hypotheses for evaluation, never diagnoses."
)


def esc(value) -> str:
    return str(value if value is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pct(value) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def level_color(level: str) -> str:
    return {"high": TEAL, "medium": AMBER, "low": RED}.get(str(level or "").lower(), CYAN)


def meter(value: float, color: str) -> str:
    return f'<div class="meter"><i style="width:{pct(value) * 100:.1f}%;background:{color}"></i></div>'


def items(rows, css: str = "fx") -> str:
    rows = [str(r) for r in (rows or []) if str(r).strip()]
    if not rows:
        return ""
    return f'<ul class="{css}">' + "".join(f"<li>{esc(r)}</li>" for r in rows) + "</ul>"


def kv(key: str, value, tone: str = "") -> str:
    if isinstance(value, bool):
        shown, cls = ("Pass", "ok") if value else ("Fail", "bad")
    elif isinstance(value, float) and 0.0 <= value <= 1.0:
        shown, cls = f"{value:.0%}", tone
    elif value is None:
        shown, cls = "n/a", ""
    else:
        shown, cls = esc(value), tone
    return f'<div class="kv"><span class="k">{esc(key)}</span><span class="v {cls}">{shown}</span></div>'


def section(title: str, count: str = "", first: bool = False) -> None:
    cls = ' class="sec first"' if first else ' class="sec"'
    n = f'<span class="n">{esc(count)}</span>' if count else ""
    st.markdown(f'<div{cls}><h2>{esc(title)}</h2><span class="line"></span>{n}</div>',
                unsafe_allow_html=True)


def load_case(text: str) -> None:
    st.session_state["clinical_text"] = text


# ── Charts (hand-built SVG, no plotting library) ─────────────────────────────

def chart_confidence(hypotheses) -> str:
    """Horizontal bars: model confidence per hypothesis."""
    if not hypotheses:
        return '<div class="small">No hypotheses to chart.</div>'
    rows = []
    for hyp in hypotheses:
        level = str(hyp.get("confidence_level") or "").lower()
        color = level_color(level)
        value = float(hyp.get("confidence") or 0.0)
        name = str(hyp.get("condition") or "Unknown")
        label = esc(name if len(name) <= 30 else name[:29] + "\u2026")
        rows.append(
            f'<div class="barrow"><span class="lb" title="{esc(name)}">{label}</span>'
            f'<span class="track"><span class="fill" style="width:{pct(value) * 100:.1f}%;'
            f'background:{color}"></span></span>'
            f'<span class="val">{value:.0%}</span></div>'
        )
    return "".join(rows)


def chart_trust(trust: dict) -> str:
    """Grouped bars: the four trust components on a shared 0-100% scale."""
    fields = [
        ("Source reliability", trust.get("source_reliability"), CYAN),
        ("Citation validity", trust.get("citation_validity"), TEAL),
        ("Grounded claims", trust.get("grounded_claim_rate"), TEAL),
        ("Evidence relevance", trust.get("evidence_relevance"), CYAN),
    ]
    rows = []
    for label, value, color in fields:
        number = pct(value) * 100
        rows.append(
            f'<div class="barrow"><span class="lb">{esc(label)}</span>'
            f'<span class="track"><span class="fill" style="width:{number:.1f}%;'
            f'background:{color}"></span></span>'
            f'<span class="val">{number:.0f}%</span></div>'
        )
    return "".join(rows)


def chart_sources(evidence) -> str:
    """Stem plot of rerank relevance per source, with the rerank logit labelled."""
    if not evidence:
        return '<div class="small">No sources to chart.</div>'

    width, height = 520, 150
    pad_l, pad_r, pad_t, pad_b = 26, 8, 14, 26
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    scores = []
    for src in evidence:
        raw = float(src.get("relevance_score") or 0.0)
        norm = src.get("relevance_normalized")
        if norm is None:
            norm = 1.0 / (1.0 + pow(2.718281828, -raw))
        scores.append((src, raw, pct(norm)))

    top = max(s[2] for s in scores) or 1.0
    scale = top * 1.15
    step = plot_w / max(1, len(scores))

    parts = []
    # horizontal gridlines
    for frac in (0.0, 0.5, 1.0):
        y = pad_t + plot_h - (frac * plot_h)
        parts.append(
            f'<line class="grid-line" x1="{pad_l}" y1="{y:.1f}" '
            f'x2="{width - pad_r}" y2="{y:.1f}"/>'
        )
        parts.append(
            f'<text class="axis" x="{pad_l - 5}" y="{y + 3:.1f}" text-anchor="end">'
            f'{frac * scale * 100:.0f}</text>'
        )

    for i, (src, raw, norm) in enumerate(scores):
        cx = pad_l + step * (i + 0.5)
        bar_h = (norm / scale) * plot_h if scale else 0.0
        y = pad_t + plot_h - bar_h
        parts.append(
            f'<rect x="{cx - min(11, step * 0.22):.1f}" y="{y:.1f}" '
            f'width="{min(22, step * 0.44):.1f}" height="{max(1.0, bar_h):.1f}" rx="2" '
            f'fill="{TEAL}" opacity="0.75"/>'
        )
        parts.append(
            f'<text class="axis" x="{cx:.1f}" y="{height - 9}" text-anchor="middle">'
            f'S{src.get("citation_index", i + 1)}</text>'
        )
        if src.get("cited"):
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{max(6.0, y - 5):.1f}" r="2.6" fill="{AMBER}"/>'
            )

    legend = (
        f'<div class="legend"><span><i style="background:{TEAL}"></i>Normalised relevance</span>'
        f'<span><i style="background:{AMBER};border-radius:99px"></i>Cited in answer</span>'
        f'<span style="color:var(--faint)">Axis: relevance %</span></div>'
    )
    return (f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="relevance of each retrieved source">'
            + "".join(parts) + "</svg>" + legend)


def chart_retrieval(attribution: dict, evidence) -> str:
    """Ranked bars: how much each source drove the answer."""
    if not attribution:
        return '<div class="small">No attribution data.</div>'
    index_by_id = {e.get("source_id"): e.get("citation_index") for e in evidence}
    ranked = sorted(attribution.items(), key=lambda kv: kv[1], reverse=True)[:8]
    rows = []
    for doc_id, score in ranked:
        number = index_by_id.get(doc_id)
        label = f"Source {number}" if number else str(doc_id)[:24]
        value = pct(score) * 100
        rows.append(
            f'<div class="barrow"><span class="lb">{esc(label)}</span>'
            f'<span class="track"><span class="fill" style="width:{value:.1f}%;'
            f'background:{TEAL}"></span></span>'
            f'<span class="val">{value:.0f}%</span></div>'
        )
    return "".join(rows)


# ── Results ──────────────────────────────────────────────────────────────────

def render_results(data: dict, elapsed_ms: int) -> None:
    evidence = data.get("evidence") or data.get("source_evidence") or []
    hypotheses = data.get("condition_hypotheses") or []
    flags = data.get("safety_flags") or []
    xai = data.get("xai") or {}
    trust = data.get("trust_metrics") or {}

    level = str(data.get("confidence_level") or "").lower()
    confidence = float(data.get("confidence_overall") or 0.0)

    # ── Summary + confidence chart ─────────────────────────────────────────
    section("Summary", first=True)
    st.markdown(
        f'<div class="card"><div class="body">'
        f'{esc(data.get("summary") or "No summary returned.")}</div>'
        f'<div class="stats">'
        f'<div class="stat"><div class="k">Confidence</div>'
        f'<div class="v" style="color:{level_color(level)}">{confidence:.0%}</div>'
        f'<div class="d">{esc(level.capitalize() if level else "unrated")}</div></div>'
        f'<div class="stat"><div class="k">Hypotheses</div><div class="v">{len(hypotheses)}</div>'
        f'<div class="d">considered</div></div>'
        f'<div class="stat"><div class="k">Sources</div><div class="v">{len(evidence)}</div>'
        f'<div class="d">retrieved</div></div>'
        f'<div class="stat"><div class="k">Runtime</div>'
        f'<div class="v">{elapsed_ms:,}<span style="font-size:0.72rem;color:var(--muted)">'
        f' ms</span></div><div class="d">end to end</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if hypotheses:
        st.markdown(
            f'<div class="card"><div class="head">Confidence by hypothesis</div>'
            f'<div class="sub2">Model confidence, colour-coded by band.</div>'
            f'{chart_confidence(hypotheses)}</div>',
            unsafe_allow_html=True,
        )

    # ── Safety flags ──────────────────────────────────────────────────────
    if flags:
        section("Safety flags", str(len(flags)))
        rows = []
        for flag in flags:
            sev = str(flag.get("severity") or "info").lower()
            if sev not in ("critical", "warning", "info"):
                sev = "info"
            title = esc(str(flag.get("flag_type", "flag")).replace("_", " ").title())
            rows.append(
                f'<div class="flag {sev}"><div class="t">{title}</div>'
                f'<div class="m">{esc(flag.get("message", ""))}</div></div>'
            )
        st.markdown("".join(rows), unsafe_allow_html=True)

    # ── Hypotheses ─────────────────────────────────────────────────────────
    if hypotheses:
        section("Condition hypotheses", str(len(hypotheses)))
        for hypothesis in hypotheses:
            hyp_level = str(hypothesis.get("confidence_level") or "").lower()
            color = level_color(hyp_level)
            value = float(hypothesis.get("confidence") or 0.0)
            refs = hypothesis.get("source_refs") or []

            parts = [
                f'<div class="hyp" style="border-left-color:{color}">'
                f'<div class="line1"><span class="nm">{esc(hypothesis.get("condition"))}</span>'
                f'<span class="tag {esc(hyp_level or "info")}">'
                f'{esc(hyp_level or "unrated")} &middot; {value:.0%}</span></div>'
                f'<div style="margin-top:0.5rem">{meter(value, color)}</div>'
            ]
            if refs:
                parts.append(
                    '<div class="refs">' + "".join(
                        f'<span class="ref">S{int(r)}</span>' for r in refs
                    ) + "</div>"
                )
            if hypothesis.get("supporting_factors"):
                parts.append('<div class="sub">Supporting</div>'
                             + items(hypothesis["supporting_factors"]))
            if hypothesis.get("against_factors"):
                parts.append('<div class="sub">Against</div>'
                             + items(hypothesis["against_factors"], "fx against"))
            if hypothesis.get("recommended_workup"):
                parts.append('<div class="sub">Suggested workup</div>'
                             + items(hypothesis["recommended_workup"], "fx workup"))
            parts.append("</div>")
            st.markdown("".join(parts), unsafe_allow_html=True)

    # ── Differential reasoning ─────────────────────────────────────────────
    reasoning = data.get("differential_reasoning") or ""
    if reasoning:
        section("Differential reasoning")
        st.markdown(f'<div class="card"><div class="body">{esc(reasoning)}</div></div>',
                    unsafe_allow_html=True)

    # ── Evidence chart + citations ─────────────────────────────────────────
    section("Sources & citations", str(len(evidence)))
    if evidence:
        stats = []
        if data.get("citations_used") is not None:
            stats.append(f"{data['citations_used']} markers")
        if data.get("citation_validity") is not None:
            stats.append(f"validity {pct(data['citation_validity']):.0%}")
        if data.get("citation_coverage") is not None:
            stats.append(f"coverage {pct(data['citation_coverage']):.0%}")

        st.markdown(
            f'<div class="card"><div class="head">Evidence relevance</div>'
            f'<div class="sub2">{" &middot; ".join(esc(s) for s in stats)}</div>'
            f'{chart_sources(evidence)}</div>',
            unsafe_allow_html=True,
        )

        for source in evidence:
            number = source.get("citation_index") or 0
            title = source.get("title") or "Untitled"
            journal = source.get("journal") or "Journal not recorded"
            year = source.get("year")
            venue = f"{journal} &middot; {year}" if year else journal

            pmid, url = source.get("pmid"), source.get("pmid_url")
            if url:
                pmid_html = f'<a href="{esc(url)}" target="_blank" rel="noopener">PMID {esc(pmid)}</a>'
            elif pmid:
                pmid_html = f"PMID {esc(pmid)}"
            else:
                pmid_html = "No PMID"

            raw = float(source.get("relevance_score") or 0.0)
            normalized = source.get("relevance_normalized")
            if normalized is None:
                normalized = 1.0 / (1.0 + pow(2.718281828, -raw))
            attribution = float(source.get("attribution_score") or 0.0)

            cited_by = source.get("cited_by") or []
            supports = (
                f'<div class="small" style="margin-top:0.5rem;color:var(--teal)">'
                f'Supports: {", ".join(esc(n) for n in cited_by)}</div>'
                if cited_by else
                '<div class="small" style="margin-top:0.5rem">Retrieved but not cited.</div>'
            )

            with st.expander(f"S{number}  {title}"):
                st.markdown(
                    f'<div class="small">{venue} &nbsp;&middot;&nbsp; {pmid_html}</div>'
                    f'<div class="kv" style="margin-top:0.6rem"><span class="k">Relevance</span>'
                    f'<span class="v">{pct(normalized):.0%}</span></div>{meter(pct(normalized), CYAN)}'
                    f'<div class="kv" style="margin-top:0.5rem"><span class="k">Attribution</span>'
                    f'<span class="v">{attribution:.0%}</span></div>{meter(attribution, TEAL)}'
                    f'<div class="sub">Excerpt relied upon</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.77rem;'
                    f'line-height:1.6;color:#BEC8D6;background:#0B0F16;'
                    f'border:1px solid var(--line);border-left:2px solid var(--teal);'
                    f'border-radius:7px;padding:0.6rem 0.75rem">'
                    f'{esc(source.get("excerpt") or "No abstract available.")}</div>'
                    f'{supports}',
                    unsafe_allow_html=True,
                )
                if url:
                    st.link_button("Open on PubMed", url)
    else:
        st.markdown('<div class="card"><div class="small">No sources retrieved.</div></div>',
                    unsafe_allow_html=True)

    # ── Explainable AI ────────────────────────────────────────────────────
    if xai:
        section("Explainable AI")
        attribution = xai.get("retrieval_attribution") or {}
        counterfactual = xai.get("counterfactual_explanation") or {}
        faithfulness = xai.get("faithfulness_score")
        consistency = xai.get("consistency_check")

        right_rows = (
            kv("Faithfulness", faithfulness)
            + kv("Consistency", consistency)
            + kv("Confidence estimate", float(xai.get("confidence_estimate") or 0.0))
        )
        if counterfactual:
            right_rows += kv("Confidence without top source",
                             float(counterfactual.get("confidence_without_source") or 0.0))
            right_rows += kv("Change in confidence",
                             f"{float(counterfactual.get('confidence_delta') or 0.0):+.1%}")

        left, right = st.columns([3, 2])
        with left:
            body = ('<div class="head">Retrieval attribution</div>'
                    '<div class="sub2">Share of the answer each source carries.</div>'
                    + chart_retrieval(attribution, evidence))
            if counterfactual.get("verdict"):
                body += (f'<div class="small" style="margin-top:0.5rem">'
                         f'{esc(counterfactual["verdict"])}</div>')
            st.markdown(f'<div class="card">{body}</div>', unsafe_allow_html=True)
        with right:
            st.markdown(f'<div class="card"><div class="head">Grounding</div>{right_rows}</div>',
                        unsafe_allow_html=True)

        unsupported = xai.get("unsupported_claims") or []
        if unsupported:
            st.markdown(
                '<div class="card"><div class="head">Claims without citation support</div>'
                f'{items(unsupported, "fx against")}</div>',
                unsafe_allow_html=True,
            )

    # ── Trust metrics ─────────────────────────────────────────────────────
    if trust:
        section("Trust metrics")
        overall = float(trust.get("overall_trust_score") or 0.0)
        tone = "high" if overall >= 0.7 else "medium" if overall >= 0.45 else "low"

        left, right = st.columns([3, 2])
        with left:
            st.markdown(
                f'<div class="card"><div class="head">Trust components</div>'
                f'<div class="sub2">Computed from this case only.</div>'
                f'{chart_trust(trust)}</div>',
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                f'<div class="card"><div class="head">Overall trust</div>'
                f'<div class="stats" style="margin-top:0.3rem">'
                f'<div class="stat"><div class="k">Score</div>'
                f'<div class="v" style="color:{level_color(tone)}">{overall:.0%}</div>'
                f'<div class="d">{esc(trust.get("overall_label") or "Unrated")}</div></div>'
                f'<div class="stat"><div class="k">Sources</div>'
                f'<div class="v">{len(evidence)}</div><div class="d">in this answer</div></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        checklist = "".join(
            kv(str(k).replace("_", " ").capitalize(), v)
            for k, v in (trust.get("checklist") or {}).items()
        )
        if checklist or trust.get("abstain_status"):
            body = checklist
            if trust.get("abstain_status"):
                body += ('<div class="flag warning" style="margin-top:0.5rem">'
                         '<div class="t">Abstention triggered</div>'
                         '<div class="m">Confidence fell below the configured threshold. '
                         'Treat the hypotheses above as insufficiently supported.</div></div>')
            st.markdown(f'<div class="card">{body}</div>', unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="small" style="margin-top:0.9rem;padding-top:0.7rem;'
        f'border-top:1px solid var(--line);color:var(--faint)">'
        f'case {esc(data.get("case_id", ""))} &nbsp;&middot;&nbsp; '
        f'{data.get("retrieval_count", 0)} documents retrieved &nbsp;&middot;&nbsp; '
        f'{esc(data.get("model_used", ""))} via {esc(data.get("provider") or "n/a")}</div>'
        f'<div class="small" style="margin-top:0.35rem;color:#E7C288">{esc(DISCLAIMER)}</div>',
        unsafe_allow_html=True,
    )


# ── App ──────────────────────────────────────────────────────────────────────

st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="side-h">Sample cases</div>', unsafe_allow_html=True)
    for label, text in CASES.items():
        st.button(label, key=f"case_{label}", on_click=load_case, args=(text,))

    st.markdown("---")
    st.markdown('<div class="side-h">Analysis</div>', unsafe_allow_html=True)
    include_xai = st.checkbox("Include explainable AI", value=True)
    include_trust = st.checkbox("Include trust metrics", value=True)

    with st.expander("API URL"):
        api_url = st.text_input("API", value="http://localhost:8000").rstrip("/")

    with st.expander("About"):
        st.markdown(
            "Retrieval combines dense vectors (FAISS) with lexical scoring (BM25), fused with "
            "reciprocal rank fusion and reranked by a cross-encoder.\n\n"
            "Each claim carries a citation marker that resolves to a retrieved record. Markers "
            "referencing a source that was never retrieved are removed before display."
        )

st.markdown(
    '<div class="top"><div><h1>Clinical Intelligence System</h1>'
    '<p>Research tool with explainable AI and trust evaluation</p></div>'
    '<div class="note">Research only</div></div>',
    unsafe_allow_html=True,
)

if "consented" not in st.session_state:
    st.session_state["consented"] = False

if not st.session_state["consented"]:
    section("Consent required", first=True)
    st.markdown(
        '<div class="card"><div class="body">This is a research prototype, not a clinical '
        "device. Continuing acknowledges that:</div>"
        '<ul class="fx" style="margin-top:0.5rem">'
        "<li>Case text is transmitted to a third-party hosted language model.</li>"
        "<li>Processing may occur outside your jurisdiction.</li>"
        "<li>Do not enter protected health information; the sample cases are synthetic.</li>"
        "<li>Results are hypotheses for evaluation, never diagnoses.</li>"
        "</ul></div>",
        unsafe_allow_html=True,
    )
    if st.button("I consent and continue", type="primary"):
        st.session_state["consented"] = True
        st.rerun()
    st.stop()

section("Clinical case", first=True)
clinical_text = st.text_area(
    "Presentation, vital signs, examination findings and relevant history",
    key="clinical_text",
    height=150,
    placeholder="65-year-old male with three days of fever, productive cough and pleuritic "
                "chest pain. Temperature 38.9 C, HR 110, SpO2 92% on room air...",
    label_visibility="collapsed",
)

if st.button("Analyze case", type="primary"):
    if not (clinical_text or "").strip():
        st.warning("Enter a clinical case description first.")
    else:
        outcome: dict = {}

        def _post(payload):
            try:
                outcome["response"] = requests.post(
                    f"{api_url}/api/v1/analyze", json=payload, timeout=180
                )
            except Exception as exc:
                outcome["error"] = exc

        worker = threading.Thread(
            target=_post,
            args=({
                "clinical_text": clinical_text,
                "include_xai": include_xai,
                "include_trust": include_trust,
                "deep_mode": False,
            },),
            daemon=True,
        )
        worker.start()

        slot = st.empty()
        started = time.time()
        while worker.is_alive():
            slot.markdown(
                '<div class="card" style="border-color:rgba(45,212,191,0.3)">'
                '<div class="body" style="color:var(--teal)">Analyzing case&hellip;</div></div>',
                unsafe_allow_html=True,
            )
            time.sleep(0.7)
        worker.join()
        slot.empty()

        if "error" in outcome:
            st.error(f"Could not reach the backend at {api_url}. ({outcome['error']})")
        else:
            response = outcome.get("response")
            if response is not None and response.status_code == 200:
                st.session_state["last_result"] = (
                    response.json(), int((time.time() - started) * 1000)
                )
            else:
                status = response.status_code if response is not None else "no response"
                body = response.text[:300] if response is not None else ""
                st.error(f"Analysis failed ({status}): {body}")

if "last_result" in st.session_state:
    payload, elapsed = st.session_state["last_result"]
    render_results(payload, elapsed)

with st.expander("Ethics evaluation results"):
    results_dir = "evaluation/results"
    if os.path.isdir(results_dir):
        import json

        for fname in sorted(os.listdir(results_dir)):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(results_dir, fname), "r", encoding="utf-8") as handle:
                        st.markdown(f"**{fname}**")
                        st.json(json.load(handle))
                except Exception:
                    pass
    else:
        st.caption("No evaluation results yet. Run the ethics study first.")