"""
CVD Risk Intelligence Platform — Streamlit Clinical Dashboard
Interactive UI for clinicians to assess patient CVD risk.

Run: streamlit run dashboard.py
"""

from __future__ import annotations

import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Page config (MUST be first Streamlit call) ─────────────────
st.set_page_config(
    page_title="CVD Risk Intelligence Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ──────────────────────────────────────────────────────
MODEL_PATH   = Path("outputs/06_machine_learning/models/best_model.pkl")
METRICS_PATH = Path("outputs/06_machine_learning/metrics/model_metrics.json")
SCALERS_PATH = Path("outputs/03_preprocessing/scalers.pkl")
FEAT_PATH    = Path("outputs/06_machine_learning/feature_columns.json")
AUDIT_PATH   = Path("outputs/15_audit/audit_trail.jsonl")
XAI_PATH     = Path("outputs/07_xai/xai_summary.json")
STATS_PATH   = Path("outputs/05_statistics/statistical_summary.json")


# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark clinical theme */
  .main { background-color: #0f1923; }
  .stApp { background-color: #0f1923; }

  .metric-card {
    background: linear-gradient(135deg, #1e2d3d, #16232f);
    border: 1px solid #2c3e50;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 4px;
  }
  .metric-val   { font-size: 2.2rem; font-weight: 700; }
  .metric-label { font-size: 0.78rem; color: #7fb3d3; text-transform: uppercase; letter-spacing: .06em; }
  .metric-sub   { font-size: 0.72rem; color: #556b7d; margin-top: 4px; }

  .risk-high     { color: #e74c3c !important; }
  .risk-moderate { color: #e67e22 !important; }
  .risk-low      { color: #27ae60 !important; }

  .risk-banner-high     { background: linear-gradient(90deg,#7b1a1a,#c0392b); border-radius:10px; padding:20px; color:white; }
  .risk-banner-moderate { background: linear-gradient(90deg,#7b4a00,#d68910); border-radius:10px; padding:20px; color:white; }
  .risk-banner-low      { background: linear-gradient(90deg,#0d5c2e,#1e8449); border-radius:10px; padding:20px; color:white; }

  .factor-tag {
    display:inline-block; padding:4px 10px; border-radius:14px;
    font-size:.8rem; margin:3px; font-weight:600;
  }
  .factor-high { background:#fdedec; color:#c0392b; border:1px solid #e74c3c; }
  .factor-mod  { background:#fef9e7; color:#d68910; border:1px solid #f39c12; }
  .factor-norm { background:#eafaf1; color:#27ae60; border:1px solid #2ecc71; }

  .section-header {
    font-size:1rem; font-weight:700; color:#7fb3d3;
    text-transform:uppercase; letter-spacing:.08em;
    border-left:3px solid #3498db; padding-left:10px; margin:16px 0 8px;
  }
  div[data-testid="stSidebar"] { background-color: #16232f; }
  .stButton>button {
    background: linear-gradient(90deg,#2980b9,#3498db);
    color: white; border: none; border-radius: 8px;
    padding: 10px 24px; font-weight: 700; font-size: 1rem; width: 100%;
  }
  .stButton>button:hover { background: linear-gradient(90deg,#1f618d,#2980b9); }
</style>
""", unsafe_allow_html=True)


# ── Load artifacts (cached) ────────────────────────────────────
@st.cache_resource
def load_artifacts():
    if not MODEL_PATH.exists():
        return None, None, None, None
    with MODEL_PATH.open("rb") as f:
        model_art = pickle.load(f)
    with SCALERS_PATH.open("rb") as f:
        scalers = pickle.load(f)
    with METRICS_PATH.open() as f:
        metrics = json.load(f)
    with FEAT_PATH.open() as f:
        feat_cols = json.load(f)["features"]
    return model_art, scalers, metrics, feat_cols


@st.cache_data
def load_stats():
    if STATS_PATH.exists():
        return json.loads(STATS_PATH.read_text())
    return {}


def load_audit(n: int = 20) -> list[dict]:
    if not AUDIT_PATH.exists():
        return []
    lines = AUDIT_PATH.read_text().splitlines()
    return [json.loads(l) for l in lines if l.strip()][-n:]


# ── Prediction logic ───────────────────────────────────────────
def predict_patient(inputs: dict, model_art, scalers, feat_cols) -> tuple[float, int]:
    # Check if we are using the new excel dataset (contains sbp_avg, dbp_avg, sex, etc.)
    is_excel = any(c in feat_cols for c in ["sbp_avg", "dbp_avg", "sex"])
    
    if is_excel:
        # Map values to Excel dataset features
        # gender in inputs: 1 = Female, 2 = Male. Map to 0 (Female), 1 (Male)
        sex_val = 1.0 if inputs["gender"] == 2 else 0.0
        # glucose mapping: the form gives 1, 2, 3. Map to typical mg/dL values: 1->95, 2->125, 3->180
        bg_val = 95.0 if inputs["gluc"] == 1 else 125.0 if inputs["gluc"] == 2 else 180.0
        # smoking: 0 = non-smoker, 1 = smoker
        smoke_val = float(inputs["smoke"])
        
        row = {
            "patient_id": 0.0,
            "age": float(inputs["age"]),
            "sex": sex_val,
            "education": 1.0,        # 'primary' -> 1
            "marital_status": 1.0,   # 'married' -> 1
            "occupation": 1.0,       # 'self-employed' -> 1
            "sbp_avg": float(inputs["ap_hi"]),
            "dbp_avg": float(inputs["ap_lo"]),
            "bg_mgdl": bg_val,
            "bmi": inputs["weight"] / ((inputs["height"] / 100) ** 2),
            "smoking": smoke_val,
            "village": 1.0,          # 'jango' -> 1
            "areas": 1.0,            # 'rural' -> 1
            "bplt": 0.0,             # 'No' -> 0
            "lltt": 0.0,             # 'No' -> 0
            "aptt": 0.0,             # 'No' -> 0
            "pulse_pressure": float(inputs["ap_hi"] - inputs["ap_lo"]),
            "age_decade": float(int(inputs["age"] // 10)),
        }
    else:
        # Original CSV dataset mapping
        age_days = inputs["age"] * 365.25
        bmi = inputs["weight"] / ((inputs["height"] / 100) ** 2)
        pulse_pressure = inputs["ap_hi"] - inputs["ap_lo"]
        age_decade = float(int(inputs["age"] // 10))

        row = {
            "id": 0.0, "age": age_days, "gender": float(inputs["gender"]),
            "height": float(inputs["height"]), "weight": float(inputs["weight"]),
            "ap_hi": float(inputs["ap_hi"]), "ap_lo": float(inputs["ap_lo"]),
            "cholesterol": float(inputs["cholesterol"]), "gluc": float(inputs["gluc"]),
            "smoke": float(inputs["smoke"]), "alco": float(inputs["alco"]),
            "active": float(inputs["active"]),
            "pulse_pressure": float(pulse_pressure), "bmi": float(bmi),
            "age_decade": age_decade,
        }
        
    df = pd.DataFrame([row])
    for col in feat_cols:
        if col not in df.columns:
            df[col] = 0.0
    df = df[feat_cols].copy()

    for name, info in scalers.items():
        cols = [c for c in info["columns"] if c in df.columns]
        if cols:
            df[cols] = info["scaler"].transform(df[cols])

    model = model_art["model"]
    prob = float(model.predict_proba(df)[0][1])
    pred = int(prob >= 0.5)
    return prob, pred


def risk_color(prob: float) -> str:
    if prob >= 0.65: return "#e74c3c"
    if prob >= 0.45: return "#e67e22"
    return "#27ae60"


def risk_label(prob: float) -> str:
    if prob >= 0.75: return "HIGH RISK"
    if prob >= 0.55: return "MODERATE-HIGH"
    if prob >= 0.40: return "MODERATE"
    return "LOW RISK"


def risk_class(prob: float) -> str:
    if prob >= 0.55: return "high"
    if prob >= 0.40: return "moderate"
    return "low"


def write_audit(event: str, data: dict):
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event_type": event, "timestamp": datetime.now(timezone.utc).isoformat(), **data}
    with AUDIT_PATH.open("a") as f:
        f.write(json.dumps(entry, default=str) + "\n")


# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 CVD Risk Platform")
    st.markdown("*Australian Healthcare Compliant*")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["🩺 Patient Assessment", "📊 Model Dashboard",
         "📐 Statistical Insights", "📋 Audit Trail",
         "📁 Report Gallery"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    model_art, scalers, metrics, feat_cols = load_artifacts()
    if model_art:
        best = metrics.get("best_model", {})
        st.markdown(f"**Model:** {model_art.get('model_name','N/A')}")
        st.markdown(f"**ROC-AUC:** `{best.get('roc_auc','N/A')}`")
        st.markdown(f"**Status:** 🟢 Online")
    else:
        st.error("⚠️ Model not loaded. Run Agent 6 first.")

    st.markdown("---")
    st.markdown("*v1.0 | KFUPM PhD + Liverpool MSc*")


# ══════════════════════════════════════════════════════════════
# PAGE 1: PATIENT ASSESSMENT
# ══════════════════════════════════════════════════════════════
if page == "🩺 Patient Assessment":
    st.markdown("# 🩺 Patient CVD Risk Assessment")
    st.markdown("Enter patient measurements below. All fields required. **Results are decision-support only — not a clinical diagnosis.**")

    if not model_art:
        st.error("Model not available. Run the full pipeline first.")
        st.stop()

    # ── Input form ──────────────────────────────────────────
    with st.form("patient_form"):
        st.markdown('<div class="section-header">👤 Patient Demographics</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        age    = c1.number_input("Age (years)", 18, 100, 55)
        gender = c2.selectbox("Gender", [1, 2], format_func=lambda x: "Female" if x == 1 else "Male")
        height = c3.number_input("Height (cm)", 100, 220, 170)
        weight = c1.number_input("Weight (kg)", 20.0, 200.0, 80.0, step=0.5)
        bmi_display = weight / ((height / 100) ** 2)
        c2.metric("BMI (calculated)", f"{bmi_display:.1f}")

        st.markdown('<div class="section-header">❤️ Cardiovascular Measurements</div>', unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        ap_hi       = c4.number_input("Systolic BP (mmHg)", 60, 250, 130)
        ap_lo       = c5.number_input("Diastolic BP (mmHg)", 40, 180, 85)
        pp_display  = ap_hi - ap_lo
        c6.metric("Pulse Pressure", f"{pp_display} mmHg")
        cholesterol = c4.selectbox("Cholesterol", [1, 2, 3],
                                   format_func=lambda x: {1:"Normal",2:"Above Normal",3:"Well Above Normal"}[x])
        gluc        = c5.selectbox("Glucose", [1, 2, 3],
                                   format_func=lambda x: {1:"Normal",2:"Above Normal",3:"Well Above Normal"}[x])

        st.markdown('<div class="section-header">🚬 Lifestyle Factors</div>', unsafe_allow_html=True)
        c7, c8, c9 = st.columns(3)
        smoke  = c7.selectbox("Smoking", [0, 1], format_func=lambda x: "Non-Smoker" if x == 0 else "Smoker")
        alco   = c8.selectbox("Alcohol", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        active = c9.selectbox("Physical Activity", [0, 1], format_func=lambda x: "Sedentary" if x == 0 else "Active")

        submitted = st.form_submit_button("🔍 Assess CVD Risk", use_container_width=True)

    # ── Results ─────────────────────────────────────────────
    if submitted:
        if ap_hi <= ap_lo:
            st.error("⚠️ Systolic BP must be greater than Diastolic BP.")
            st.stop()

        inputs = dict(age=age, gender=gender, height=height, weight=weight,
                      ap_hi=ap_hi, ap_lo=ap_lo, cholesterol=cholesterol,
                      gluc=gluc, smoke=smoke, alco=alco, active=active)

        with st.spinner("Analysing patient data..."):
            prob, pred = predict_patient(inputs, model_art, scalers, feat_cols)

        rc = risk_class(prob)
        rl = risk_label(prob)
        color = risk_color(prob)

        # ── Risk Banner ──────────────────────────────────────
        st.markdown(f"""
        <div class="risk-banner-{rc}">
          <div style="font-size:1.8rem;font-weight:700">
            {"⚠️" if rc!="low" else "✅"} {rl} — CVD Probability: {prob*100:.1f}%
          </div>
          <div style="opacity:.85;margin-top:6px">
            {"This patient has elevated cardiovascular risk. Clinical review recommended." if rc!="low"
             else "Risk factors within acceptable range. Routine monitoring advised."}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # ── Gauge + Metrics ──────────────────────────────────
        col_g, col_m = st.columns([1, 2])

        with col_g:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(prob * 100, 1),
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "CVD Risk %", "font": {"size": 16, "color": "#ecf0f1"}},
                number={"suffix": "%", "font": {"size": 32, "color": color}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#7fb3d3"}},
                    "bar": {"color": color, "thickness": 0.3},
                    "bgcolor": "#1e2d3d",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40],  "color": "#0d5c2e"},
                        {"range": [40, 65], "color": "#7b4a00"},
                        {"range": [65, 100],"color": "#7b1a1a"},
                    ],
                    "threshold": {"line": {"color": "white", "width": 3},
                                  "thickness": 0.8, "value": prob * 100},
                },
            ))
            gauge.update_layout(
                paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
                height=280, margin=dict(t=40, b=10, l=20, r=20),
                font={"color": "#ecf0f1"}
            )
            st.plotly_chart(gauge, use_container_width=True)

        with col_m:
            best = metrics.get("best_model", {})
            kpis = [
                ("Prediction", "CVD+" if pred == 1 else "CVD−", color),
                ("Probability", f"{prob*100:.1f}%", color),
                ("Model", model_art.get("model_name", "N/A"), "#3498db"),
                ("ROC-AUC", str(best.get("roc_auc", "N/A")), "#9b59b6"),
                ("Sensitivity", str(best.get("sensitivity", "N/A")), "#27ae60"),
                ("BMI", f"{bmi_display:.1f}", "#e67e22"),
            ]
            rows = [kpis[:3], kpis[3:]]
            for row in rows:
                cols = st.columns(3)
                for i, (label, val, c) in enumerate(row):
                    cols[i].markdown(f"""
                    <div class="metric-card">
                      <div class="metric-val" style="color:{c}">{val}</div>
                      <div class="metric-label">{label}</div>
                    </div>""", unsafe_allow_html=True)

        # ── Risk Factors ─────────────────────────────────────
        st.markdown('<div class="section-header">🔍 Risk Factor Analysis</div>', unsafe_allow_html=True)

        factor_cols = st.columns(2)
        factors_left = []
        factors_right = []

        def make_factor(label, val_str, status):
            cls = "high" if status == "HIGH" else "mod" if status == "ELEVATED" else "norm"
            icon = "🔴" if cls == "high" else "🟡" if cls == "mod" else "🟢"
            return f'<span class="factor-tag factor-{cls}">{icon} {label}: {val_str}</span>'

        factors_left.append(make_factor("Systolic BP",
            f"{ap_hi} mmHg", "HIGH" if ap_hi >= 140 else "ELEVATED" if ap_hi >= 130 else "NORMAL"))
        factors_left.append(make_factor("Diastolic BP",
            f"{ap_lo} mmHg", "HIGH" if ap_lo >= 90 else "ELEVATED" if ap_lo >= 80 else "NORMAL"))
        factors_left.append(make_factor("Cholesterol",
            {1:"Normal",2:"Above Normal",3:"Well Above Normal"}[cholesterol],
            "HIGH" if cholesterol == 3 else "ELEVATED" if cholesterol == 2 else "NORMAL"))
        factors_left.append(make_factor("Glucose",
            {1:"Normal",2:"Above Normal",3:"Well Above Normal"}[gluc],
            "HIGH" if gluc == 3 else "ELEVATED" if gluc == 2 else "NORMAL"))

        factors_right.append(make_factor("BMI",
            f"{bmi_display:.1f}", "HIGH" if bmi_display >= 30 else "ELEVATED" if bmi_display >= 25 else "NORMAL"))
        factors_right.append(make_factor("Pulse Pressure",
            f"{pp_display} mmHg", "HIGH" if pp_display >= 60 else "ELEVATED" if pp_display >= 50 else "NORMAL"))
        factors_right.append(make_factor("Smoking",
            "Active Smoker" if smoke else "Non-Smoker",
            "HIGH" if smoke else "NORMAL"))
        factors_right.append(make_factor("Activity",
            "Sedentary" if not active else "Active",
            "ELEVATED" if not active else "NORMAL"))

        with factor_cols[0]:
            st.markdown(" ".join(factors_left), unsafe_allow_html=True)
        with factor_cols[1]:
            st.markdown(" ".join(factors_right), unsafe_allow_html=True)

        # ── Clinical Recommendation ───────────────────────────
        st.markdown('<div class="section-header">📋 Clinical Recommendation (AI-Assisted)</div>', unsafe_allow_html=True)
        if prob >= 0.75:
            st.error(f"""**URGENT — HIGH CVD RISK**

• Immediate cardiology referral recommended
• {"Hypertension management required (BP: {ap_hi}/{ap_lo} mmHg)" if ap_hi >= 140 else ""}
• {"Lipid-lowering therapy assessment (Cholesterol: elevated)" if cholesterol >= 2 else ""}
• {"Smoking cessation program — urgent priority" if smoke else ""}
• {"Supervised exercise program recommended" if not active else ""}
• Full cardiovascular workup per Australian Heart Foundation guidelines
• Repeat risk assessment in 3 months after intervention

⚕️ *This is AI-generated decision support. Clinical judgement must prevail.*""")
        elif prob >= 0.45:
            st.warning(f"""**ELEVATED CVD RISK — Action Required**

• Cardiology consultation within 4–6 weeks
• Blood pressure monitoring (current: {ap_hi}/{ap_lo} mmHg)
• Fasting lipid panel recommended
• Lifestyle modification counselling
• Consider statin therapy per NHFA guidelines
• Follow-up in 3 months

⚕️ *This is AI-generated decision support. Clinical judgement must prevail.*""")
        else:
            st.success(f"""**LOW CVD RISK — Routine Monitoring**

• Annual cardiovascular health review with GP
• Continue healthy lifestyle habits
• {'Consider smoking cessation support' if smoke else 'Maintain non-smoking status'}
• Maintain physical activity levels
• Repeat risk assessment annually or if risk factors change

⚕️ *This is AI-generated decision support. Clinical judgement must prevail.*""")

        # ── Write audit ───────────────────────────────────────
        write_audit("DASHBOARD_PREDICTION", {
            "cvd_risk": pred,
            "cvd_probability": round(prob, 4),
            "risk_level": rl,
            "model": model_art.get("model_name"),
            "demographic_age_group": f"{int(age//10)*10}s",
        })


# ══════════════════════════════════════════════════════════════
# PAGE 2: MODEL DASHBOARD
# ══════════════════════════════════════════════════════════════
elif page == "📊 Model Dashboard":
    st.markdown("# 📊 Model Performance Dashboard")

    if not metrics:
        st.error("Metrics not available. Run Agent 6 first.")
        st.stop()

    best = metrics["best_model"]
    all_models = metrics["all_models"]
    sorted_models = sorted(all_models, key=lambda x: x["roc_auc"], reverse=True)

    # ── Top KPIs ──────────────────────────────────────────
    k = st.columns(5)
    kpi_data = [
        ("Best Model",    best.get("model_name", best.get("model", "N/A")), "#3498db"),
        ("ROC-AUC",       f"{best.get('roc_auc','N/A')}", "#27ae60"),
        ("Sensitivity",   f"{best.get('sensitivity','N/A')}", "#e67e22"),
        ("Specificity",   f"{best.get('specificity','N/A')}", "#9b59b6"),
        ("F1 Score",      f"{best.get('f1_score','N/A')}", "#e74c3c"),
    ]
    for i, (label, val, color) in enumerate(kpi_data):
        k[i].markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:{color};font-size:1.6rem">{val}</div>
          <div class="metric-label">{label}</div></div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Charts ────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="ROC-AUC", x=[m["model"] for m in sorted_models],
            y=[m["roc_auc"] for m in sorted_models],
            marker_color=["#27ae60" if m["model"] == best.get("model") else "#3498db" for m in sorted_models]
        ))
        fig.add_trace(go.Bar(
            name="F1 Score", x=[m["model"] for m in sorted_models],
            y=[m["f1_score"] for m in sorted_models], marker_color="#9b59b6"
        ))
        fig.update_layout(
            title="Model Benchmark — ROC-AUC vs F1", barmode="group",
            paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
            font={"color": "#ecf0f1"}, height=380,
            xaxis={"tickangle": -30, "gridcolor": "#253647"},
            yaxis={"range": [0.55, 0.9], "gridcolor": "#253647"},
            legend={"font": {"color": "#7fb3d3"}},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cm = best.get("confusion_matrix", {})
        tp, tn, fp, fn = cm.get("TP",0), cm.get("TN",0), cm.get("FP",0), cm.get("FN",0)
        fig2 = go.Figure(go.Heatmap(
            z=[[tn, fp], [fn, tp]],
            x=["Predicted: No CVD", "Predicted: CVD"],
            y=["Actual: No CVD", "Actual: CVD"],
            text=[[f"TN<br>{tn:,}", f"FP<br>{fp:,}"],
                  [f"FN⚠<br>{fn:,}", f"TP<br>{tp:,}"]],
            texttemplate="%{text}", textfont={"size": 14},
            colorscale=[[0,"#1e2d3d"],[0.5,"#2980b9"],[1,"#27ae60"]],
            showscale=False,
        ))
        fig2.update_layout(
            title="Confusion Matrix — Best Model",
            paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
            font={"color": "#ecf0f1"}, height=380,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Full leaderboard table ─────────────────────────────
    st.markdown('<div class="section-header">🏆 Full Model Leaderboard</div>', unsafe_allow_html=True)
    df_table = pd.DataFrame([{
        "Model": ("🏆 " if m["model"] == best.get("model") else "") + m["model"],
        "ROC-AUC": m["roc_auc"],
        "F1": m["f1_score"],
        "Accuracy": m["accuracy"],
        "Sensitivity": m["sensitivity"],
        "Specificity": m["specificity"],
        "MCC": m["mcc"],
        "False Neg ⚠": m["confusion_matrix"]["FN"],
    } for m in sorted_models])
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-header">📋 Model Card</div>', unsafe_allow_html=True)
    model_card = Path("outputs/06_machine_learning/model_card.md")
    if model_card.exists():
        st.markdown(model_card.read_text())


# ══════════════════════════════════════════════════════════════
# PAGE 3: STATISTICAL INSIGHTS
# ══════════════════════════════════════════════════════════════
elif page == "📐 Statistical Insights":
    st.markdown("# 📐 Statistical Analysis")
    stats = load_stats()
    if not stats:
        st.error("Stats not available. Run Agent 5 first.")
        st.stop()

    ttest = stats.get("ttest_mannwhitney", [])
    sig = [r for r in ttest if r.get("u_significant")]

    st.info(f"**{len(sig)} of {len(ttest)} features** are statistically significant (Mann-Whitney U, p < 0.05)")

    sorted_ttest = sorted(ttest, key=lambda x: x["u_p"])[:15]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="CVD+", x=[r["feature"] for r in sorted_ttest],
        y=[r["mean_cvd_pos"] for r in sorted_ttest], marker_color="#e74c3c",
    ))
    fig.add_trace(go.Bar(
        name="CVD−", x=[r["feature"] for r in sorted_ttest],
        y=[r["mean_cvd_neg"] for r in sorted_ttest], marker_color="#3498db",
    ))
    fig.update_layout(
        title="Feature Means: CVD+ vs CVD− (sorted by significance)",
        barmode="group", paper_bgcolor="#1e2d3d", plot_bgcolor="#1e2d3d",
        font={"color": "#ecf0f1"}, height=420,
        xaxis={"tickangle": -30, "gridcolor": "#253647"},
        yaxis={"gridcolor": "#253647"},
        legend={"font": {"color": "#7fb3d3"}},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Statistical Test Results</div>', unsafe_allow_html=True)
    df_stats = pd.DataFrame([{
        "Feature": r["feature"],
        "Mean (CVD+)": round(r["mean_cvd_pos"], 3),
        "Mean (CVD−)": round(r["mean_cvd_neg"], 3),
        "U p-value": r["u_p"],
        "Significant": "✅" if r.get("u_significant") else "—",
        "T p-value": r["t_p"],
    } for r in sorted_ttest])
    st.dataframe(df_stats, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE 4: AUDIT TRAIL
# ══════════════════════════════════════════════════════════════
elif page == "📋 Audit Trail":
    st.markdown("# 📋 Audit Trail")
    st.markdown("*Immutable log of all platform events — Australian Privacy Act compliant*")

    entries = load_audit(50)
    if not entries:
        st.info("No audit entries yet. Run the pipeline or make a prediction.")
    else:
        st.success(f"**{len(entries)} recent entries** | Audit file: `{AUDIT_PATH}`")
        df_audit = pd.DataFrame([{
            "Timestamp": e.get("timestamp","")[:19].replace("T"," "),
            "Event": e.get("event_type",""),
            "Details": str({k: v for k, v in e.items()
                           if k not in ["event_type","timestamp"]})[:100],
        } for e in reversed(entries)])
        st.dataframe(df_audit, use_container_width=True, hide_index=True)

        pred_events = [e for e in entries if "PREDICTION" in e.get("event_type","")]
        if pred_events:
            st.markdown('<div class="section-header">Prediction Summary</div>', unsafe_allow_html=True)
            high = sum(1 for e in pred_events if e.get("cvd_risk") == 1)
            low  = sum(1 for e in pred_events if e.get("cvd_risk") == 0)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Predictions", len(pred_events))
            c2.metric("High Risk (CVD+)", high)
            c3.metric("Low Risk (CVD−)", low)


# ══════════════════════════════════════════════════════════════
# PAGE 5: REPORT GALLERY
# ══════════════════════════════════════════════════════════════
elif page == "📁 Report Gallery":
    st.markdown("# 📁 Platform Report Gallery")
    st.markdown("All outputs generated by the 15-agent pipeline. Open links in your browser.")

    reports = {
        "🚀 Launch Dashboard": "outputs/LAUNCH_DASHBOARD.html",
        "📊 EDA Report": "outputs/04_eda/eda_report.html",
        "🧹 Data Quality Report": "outputs/02_data_cleaning/data_quality_report.html",
        "📐 Statistical Report": "outputs/05_statistics/statistical_report.html",
        "🤖 ML Benchmark Report": "outputs/06_machine_learning/ml_report.html",
        "🧠 SHAP Explainability": "outputs/07_xai/shap_report.html",
        "🔬 LIME Explainability": "outputs/07_xai/lime_report.html",
        "✅ QC Report": "outputs/13_documentation/qc_report.html",
    }

    for name, path in reports.items():
        p = Path(path)
        exists = p.exists()
        size = f"{p.stat().st_size/1024:.0f} KB" if exists else "—"
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"**{name}**  \n`{path}`")
        col2.markdown(f"`{size}`")
        col3.markdown("✅ Ready" if exists else "⬜ Missing")

    st.markdown("---")
    st.markdown("**Model Card (Markdown)**")
    mc = Path("outputs/06_machine_learning/model_card.md")
    if mc.exists():
        with st.expander("View Model Card"):
            st.markdown(mc.read_text())
