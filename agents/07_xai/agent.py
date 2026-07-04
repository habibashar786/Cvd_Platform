"""
AGENT 7 — Explainable AI Agent
SHAP (KernelExplainer) + LIME (LimeTabularExplainer)
"""
from __future__ import annotations
import json, pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import structlog

log = structlog.get_logger()
ML_OUTPUT   = Path("outputs/06_machine_learning")
INPUT_PATH  = Path("outputs/03_preprocessing/processed_dataset.parquet")
OUTPUT_DIR  = Path("outputs/07_xai")


def _load_artifacts():
    best_model_path = ML_OUTPUT / "models/best_model.pkl"
    if not best_model_path.exists():
        raise FileNotFoundError("Best model not found. Run Agent 6 first.")
    with best_model_path.open("rb") as f:
        artifact = pickle.load(f)
    df = pd.read_parquet(INPUT_PATH) if INPUT_PATH.exists() else pd.read_parquet(
        Path("outputs/02_data_cleaning/cleaned_dataset.parquet"))
    return artifact, df


def _safe_float(v):
    """Convert any numpy scalar/array to a plain Python float."""
    if isinstance(v, np.ndarray):
        v = v.flatten()
        return float(v[0]) if v.size == 1 else float(np.mean(v))
    if hasattr(v, "item"):
        return float(v.item())
    return float(v)


# Tree-based model class name fragments — use TreeExplainer for these
_TREE_MODELS = (
    "forest", "tree", "boost", "gbm", "xgb", "lgbm", "lightgbm",
    "catboost", "extratrees", "adaboost",
)


def _is_tree_model(model: Any) -> bool:
    name = type(model).__name__.lower()
    return any(t in name for t in _TREE_MODELS)


def _get_shap_values(model: Any, X_explain: pd.DataFrame, X_bg: pd.DataFrame):
    """
    Auto-select the best SHAP explainer for the model type.
    - TreeExplainer  → all tree/boosting models (fast, exact)
    - LinearExplainer → LogisticRegression, SVM-linear
    - KernelExplainer → fallback for anything else
    Returns (shap_values_2d, explainer_type_str)
    """
    import shap

    # ── 1. TreeExplainer (preferred for LightGBM, XGBoost, CatBoost, RF …) ──
    if _is_tree_model(model):
        log.info("Running SHAP TreeExplainer", samples=len(X_explain))
        try:
            explainer = shap.TreeExplainer(model)
            sv_raw = explainer.shap_values(X_explain)
            # TreeExplainer returns list[array] for binary → take class-1
            if isinstance(sv_raw, list):
                sv = np.array(sv_raw[1], dtype=np.float64)
            else:
                sv_arr = np.array(sv_raw, dtype=np.float64)
                sv = sv_arr[:, :, 1] if sv_arr.ndim == 3 else sv_arr
            return sv, "TreeExplainer"
        except Exception as exc:
            log.warning("TreeExplainer failed — falling back to Kernel", error=str(exc))

    # ── 2. LinearExplainer (LogisticRegression, LinearSVC …) ────────────────
    model_name = type(model).__name__.lower()
    if "logistic" in model_name or "linearsvc" in model_name:
        log.info("Running SHAP LinearExplainer", samples=len(X_explain))
        try:
            explainer = shap.LinearExplainer(model, X_bg)
            sv_raw = explainer.shap_values(X_explain)
            sv = np.array(sv_raw, dtype=np.float64)
            if sv.ndim == 3:
                sv = sv[:, :, 1]
            return sv, "LinearExplainer"
        except Exception as exc:
            log.warning("LinearExplainer failed — falling back to Kernel", error=str(exc))

    # ── 3. KernelExplainer (universal fallback — slow but works on anything) ─
    log.info("Running SHAP KernelExplainer (fallback)", samples=len(X_explain))
    # Wrap predict_proba as a plain numpy function to avoid feature_names issues
    def predict_fn(X_arr: np.ndarray) -> np.ndarray:
        return model.predict_proba(pd.DataFrame(X_arr, columns=X_bg.columns))

    explainer = shap.KernelExplainer(predict_fn, X_bg.values)
    sv_raw = explainer.shap_values(X_explain.values, nsamples=100)
    if isinstance(sv_raw, list):
        sv = np.array(sv_raw[1], dtype=np.float64)
    else:
        sv_arr = np.array(sv_raw, dtype=np.float64)
        sv = sv_arr[:, :, 1] if sv_arr.ndim == 3 else sv_arr
    return sv, "KernelExplainer"


def _run_shap(model: Any, X_sample: pd.DataFrame) -> dict:
    try:
        import shap  # noqa: F401
    except ImportError:
        log.warning("SHAP not installed — pip install shap")
        return {}

    result: dict[str, Any] = {}

    n_bg      = min(50, len(X_sample))
    n_explain = min(100, len(X_sample))
    X_bg  = X_sample.iloc[:n_bg].reset_index(drop=True)
    Xex   = X_sample.iloc[:n_explain].reset_index(drop=True)

    try:
        sv, explainer_type = _get_shap_values(model, Xex, X_bg)
        result["explainer_type"] = explainer_type
    except Exception as exc:
        log.error("All SHAP explainers failed", error=str(exc))
        return {}

    if sv.ndim == 1:
        sv = sv.reshape(1, -1)

    n_samples, n_feats = sv.shape
    cols = list(X_sample.columns[:n_feats])

    # Global importance
    mean_abs = np.abs(sv).mean(axis=0)           # (n_feats,)
    feat_imp = [(cols[i], float(mean_abs[i])) for i in range(len(cols))]
    result["global_importance"] = dict(
        sorted(feat_imp, key=lambda x: x[1], reverse=True)
    )

    # Local (patient-level)
    result["local_explanations"] = []
    for i in range(min(3, n_samples)):
        row    = sv[i]                            # (n_feats,)
        local  = {cols[j]: round(float(row[j]), 6) for j in range(len(cols))}
        s_local = dict(sorted(local.items(), key=lambda x: abs(x[1]), reverse=True))
        narrative_lines = []
        for feat, val in list(s_local.items())[:5]:
            direction = "increases" if val > 0 else "decreases"
            mag = "strongly" if abs(val) > 0.1 else "moderately" if abs(val) > 0.05 else "slightly"
            narrative_lines.append(f"- **{feat}** {mag} {direction} CVD risk (SHAP={val:+.4f})")
        result["local_explanations"].append({
            "patient_index": i,
            "top_factors": dict(list(s_local.items())[:10]),
            "clinical_narrative": "\n".join(narrative_lines)
        })

    log.info("SHAP complete", features=len(result["global_importance"]))
    return result


def _run_lime(model: Any, X_sample: pd.DataFrame) -> dict:
    try:
        import lime.lime_tabular
    except ImportError:
        log.warning("LIME not installed — pip install lime")
        return {}

    log.info("Running LIME analysis")
    explainer = lime.lime_tabular.LimeTabularExplainer(
        X_sample.values,
        feature_names=list(X_sample.columns),
        class_names=["No CVD", "CVD"],
        mode="classification",
        random_state=42,
    )
    results = []
    for i in range(min(3, len(X_sample))):
        try:
            exp = explainer.explain_instance(
                X_sample.iloc[i].values,
                model.predict_proba,
                num_features=10,
            )
            results.append({
                "patient_index": i,
                "prediction_probability": {
                    "No CVD": round(float(exp.predict_proba[0]), 4),
                    "CVD":    round(float(exp.predict_proba[1]), 4),
                },
                "feature_contributions": [
                    {"feature": feat, "weight": round(float(w), 6)}
                    for feat, w in exp.as_list()
                ],
            })
        except Exception as exc:
            log.warning("LIME patient failed", patient=i, error=str(exc))

    log.info("LIME complete", explanations=len(results))
    return {"explanations": results}


def _shap_html(shap_result: dict) -> str:
    if not shap_result:
        return "<p>SHAP not available.</p>"

    bar_data = json.dumps([
        {"feature": f, "importance": round(v, 6)}
        for f, v in list(shap_result.get("global_importance", {}).items())[:20]
    ])
    local_html = ""
    for le in shap_result.get("local_explanations", []):
        narrative = le.get("clinical_narrative", "").replace("\n", "<br>")
        local_html += f'''
        <div class="patient-card">
          <h3>Patient #{le["patient_index"] + 1}</h3>
          <div class="narrative">{narrative}</div>
        </div>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>SHAP Report</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  body{{font-family:"Segoe UI",sans-serif;max-width:1100px;margin:40px auto;color:#2c3e50}}
  h1{{border-bottom:3px solid #e74c3c;padding-bottom:12px}}
  .patient-card{{background:#fef9e7;border-left:4px solid #f39c12;padding:16px;margin:16px 0;border-radius:4px}}
  .narrative{{font-size:.9rem;line-height:1.8;margin-top:8px}}
</style></head><body>
<h1>🧠 SHAP Explainability Report — CVD Risk Platform</h1>
<p>Explainer: <strong>{shap_result.get("explainer_type","KernelExplainer")}</strong> |
Generated: {datetime.now(timezone.utc).isoformat()}</p>
<h2>Global Feature Importance (Mean |SHAP|)</h2>
<div id="shap_chart" style="height:520px"></div>
<script>
const d = {bar_data};
Plotly.newPlot("shap_chart",[{{
  type:"bar",orientation:"h",
  x:d.map(r=>r.importance), y:d.map(r=>r.feature),
  marker:{{color:d.map(r=>r.importance),colorscale:"Reds"}}
}}],{{title:"Mean |SHAP| — Global Feature Importance",height:520,
  xaxis:{{title:"Mean |SHAP value|"}}}},{{responsive:true}});
</script>
<h2>Patient-Level Clinical Explanations</h2>
{local_html}
<footer style="color:#95a5a6;font-size:.8rem;margin-top:40px">CVD Risk Intelligence Platform | Australian Healthcare Compliant</footer>
</body></html>'''


def _lime_html(lime_result: dict) -> str:
    if not lime_result:
        return "<p>LIME not available.</p>"

    patients_html = ""
    for exp in lime_result.get("explanations", []):
        pred = exp.get("prediction_probability", {})
        rows = "".join(
            f'<tr><td>{c["feature"]}</td>'
            f'<td style="color:{("#27ae60" if c["weight"]>0 else "#e74c3c")}">{c["weight"]:+.4f}</td></tr>'
            for c in exp.get("feature_contributions", [])
        )
        patients_html += f'''
        <div style="background:#f8f9fa;border-radius:8px;padding:20px;margin:16px 0">
          <h3>Patient #{exp["patient_index"]+1}</h3>
          <p>P(CVD) = <strong style="color:#e74c3c">{pred.get("CVD",0):.4f}</strong> &nbsp;|&nbsp;
             P(No CVD) = <strong style="color:#27ae60">{pred.get("No CVD",0):.4f}</strong></p>
          <table style="width:100%;border-collapse:collapse">
          <tr><th style="background:#2c3e50;color:white;padding:8px">Feature Rule</th>
              <th style="background:#2c3e50;color:white;padding:8px">LIME Weight</th></tr>
          {rows}
          </table>
        </div>'''

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>LIME Report</title>
<style>body{{font-family:"Segoe UI",sans-serif;max-width:1000px;margin:40px auto;color:#2c3e50}}
h1{{border-bottom:3px solid #9b59b6;padding-bottom:12px}}</style></head><body>
<h1>🔬 LIME Explainability Report — CVD Risk Platform</h1>
<p>{datetime.now(timezone.utc).isoformat()}</p>
{patients_html}
<footer style="color:#95a5a6;font-size:.8rem;margin-top:40px">CVD Risk Intelligence Platform</footer>
</body></html>'''


def run() -> dict[str, Any]:
    log.info("Agent 7: XAI starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        artifact, df = _load_artifacts()
    except FileNotFoundError as e:
        log.error(str(e))
        return {"success": False, "artifact": ""}

    model        = artifact["model"]
    feature_cols = artifact.get("feature_columns", [])
    target       = artifact.get("target_column", "cardio")

    X = df[feature_cols] if feature_cols else df.drop(columns=[target]).select_dtypes(include=[np.number])
    X_sample = X.sample(min(200, len(X)), random_state=42)

    shap_result = _run_shap(model, X_sample)
    lime_result = _run_lime(model, X_sample)

    (OUTPUT_DIR / "shap_report.html").write_text(_shap_html(shap_result), encoding="utf-8")
    (OUTPUT_DIR / "lime_report.html").write_text(_lime_html(lime_result), encoding="utf-8")

    with (OUTPUT_DIR / "xai_summary.json").open("w", encoding="utf-8") as f:
        json.dump({
            "shap_features": len(shap_result.get("global_importance", {})),
            "lime_patients": len(lime_result.get("explanations", [])),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)

    log.info("Agent 7 complete")
    return {"success": True, "artifact": str(OUTPUT_DIR / "shap_report.html")}


if __name__ == "__main__":
    import structlog; structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
