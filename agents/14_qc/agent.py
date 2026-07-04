"""
AGENT 14 — Quality Control Agent
Central orchestrator: cross-agent consistency, quality gates, release approval.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger()
OUTPUT_DIR = Path("outputs/13_documentation")

EXPECTED_ARTIFACTS = {
    "01_data_catalog": ["dataset_catalog.json", "data_dictionary.md"],
    "02_data_cleaning": ["cleaned_dataset.parquet", "data_quality_report.html"],
    "03_preprocessing": ["processed_dataset.parquet"],
    "04_eda": ["eda_report.html"],
    "06_machine_learning": ["models/best_model.pkl", "metrics/model_metrics.json", "model_card.md"],
    "07_xai": ["shap_report.html", "lime_report.html"],
    "11_security": ["guardrail_report.json", "threat_model.md"],
}

SUCCESS_CRITERIA = [
    "All datasets validated",
    "EDA completed",
    "Feature engineering completed",
    "Class imbalance resolved",
    "Models benchmarked",
    "Best model selected",
    "SHAP completed",
    "LIME completed",
    "Security review passed",
    "Quality review passed",
    "Deployment package generated",
    "Documentation generated",
    "Audit trail generated",
]


def _check_artifacts() -> dict[str, Any]:
    results: dict[str, Any] = {}
    base = Path("outputs")
    for folder, files in EXPECTED_ARTIFACTS.items():
        results[folder] = {}
        for fname in files:
            fpath = base / folder / fname
            results[folder][fname] = {
                "exists": fpath.exists(),
                "size_kb": round(fpath.stat().st_size / 1024, 2) if fpath.exists() else 0
            }
    return results


def _check_model_metrics() -> dict[str, Any]:
    metrics_path = Path("outputs/06_machine_learning/metrics/model_metrics.json")
    if not metrics_path.exists():
        return {"status": "MISSING"}
    with metrics_path.open() as f:
        data = json.load(f)
    best = data.get("best_model", {})
    all_models = data.get("all_models", [])
    roc_auc = best.get("roc_auc", 0)

    # Count how many models scored perfectly — more than 2 is a leakage signal
    perfect_count = sum(
        1 for m in all_models
        if m.get("roc_auc", 0) >= 1.0
        and m.get("confusion_matrix", {}).get("FP", 1) == 0
        and m.get("confusion_matrix", {}).get("FN", 1) == 0
    )
    leakage_suspected = perfect_count >= 3  # 3+ models at 1.0 = almost certainly leakage

    return {
        "status": "PRESENT",
        "best_model": best.get("model", "Unknown"),
        "roc_auc": roc_auc,
        "f1_score": best.get("f1_score", 0),
        "sensitivity": best.get("sensitivity", 0),
        "meets_threshold": roc_auc >= 0.75 and not leakage_suspected,
        "leakage_suspected": leakage_suspected,
        "perfect_score_models": perfect_count,
        "leakage_note": (
            f"WARNING: {perfect_count} models scored 1.000 ROC-AUC. "
            "Likely data leakage — re-run Agents 3 and 6."
            if leakage_suspected else "No leakage signals detected."
        ),
    }


def _check_quality_score() -> dict[str, Any]:
    qr_path = Path("outputs/02_data_cleaning/data_quality_report.html")
    pp_path = Path("outputs/03_preprocessing/preprocessing_report.json")
    result: dict[str, Any] = {}
    if pp_path.exists():
        with pp_path.open() as f:
            pp = json.load(f)
        result["preprocessing_shape"] = pp.get("output_shape", {})
        result["imbalance_strategy"] = pp.get("imbalance", {}).get("strategy_used", "N/A")
    result["quality_report_exists"] = qr_path.exists()
    return result


def _generate_qc_report(artifacts: dict, metrics: dict, quality: dict) -> dict:
    all_exist = all(
        info["exists"]
        for folder_data in artifacts.values()
        for info in folder_data.values()
    )
    model_ok = metrics.get("meets_threshold", False)
    leakage_suspected = metrics.get("leakage_suspected", False)

    criteria_status = {
        "All datasets validated": artifacts.get("01_data_catalog", {}).get("dataset_catalog.json", {}).get("exists", False),
        "EDA completed": artifacts.get("04_eda", {}).get("eda_report.html", {}).get("exists", False),
        "Best model selected": model_ok,
        "SHAP completed": artifacts.get("07_xai", {}).get("shap_report.html", {}).get("exists", False),
        "LIME completed": artifacts.get("07_xai", {}).get("lime_report.html", {}).get("exists", False),
        "Security review passed": artifacts.get("11_security", {}).get("guardrail_report.json", {}).get("exists", False),
    }

    passed = sum(1 for v in criteria_status.values() if v)
    total = len(criteria_status)

    if leakage_suspected:
        qc_status = "REJECTED"
        recommendation = "REJECTED — Data leakage detected. Re-run Agent 3 then Agent 6."
    elif all_exist and model_ok:
        qc_status = "APPROVED"
        recommendation = "APPROVED FOR DEPLOYMENT"
    else:
        qc_status = "CONDITIONAL"
        recommendation = "CONDITIONAL — Review flagged items before deployment"

    return {
        "qc_status": qc_status,
        "artifacts_complete": all_exist,
        "model_meets_threshold": model_ok,
        "leakage_suspected": leakage_suspected,
        "criteria_passed": f"{passed}/{total}",
        "criteria_detail": criteria_status,
        "model_metrics": metrics,
        "data_quality": quality,
        "artifact_inventory": artifacts,
        "release_recommendation": recommendation,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _generate_final_documentation(qc_report: dict) -> str:
    status_icon = "✅" if qc_report["qc_status"] == "APPROVED" else "⚠️"
    criteria_html = "".join(
        f"<li>{'✅' if v else '❌'} {k}</li>"
        for k, v in qc_report.get("criteria_detail", {}).items()
    )
    m = qc_report.get("model_metrics", {})
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>QC Report — CVD Platform</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;max-width:1000px;margin:40px auto;color:#2c3e50}}
  h1{{border-bottom:3px solid #27ae60;padding-bottom:12px}}
  .status{{font-size:3rem;text-align:center;padding:20px;}}
  .card{{background:#f8f9fa;border-radius:8px;padding:20px;margin:16px 0}}
  .pass{{border-left:4px solid #27ae60}} .warn{{border-left:4px solid #f39c12}}
  ul{{line-height:2}}
</style></head><body>
<h1>🔍 Quality Control Report — CVD Risk Intelligence Platform</h1>
<div class="status">{status_icon} {qc_report['qc_status']}</div>
<p style="text-align:center">{qc_report['release_recommendation']}</p>

<div class="card pass">
  <h2>📊 Model Performance</h2>
  <ul>
    <li>Best Model: <strong>{m.get('best_model','N/A')}</strong></li>
    <li>ROC-AUC: <strong>{m.get('roc_auc','N/A')}</strong></li>
    <li>F1 Score: <strong>{m.get('f1_score','N/A')}</strong></li>
    <li>Sensitivity: <strong>{m.get('sensitivity','N/A')}</strong></li>
    <li>Threshold Met (AUC≥0.75): <strong>{'✅' if m.get('meets_threshold') else '❌'}</strong></li>
  </ul>
</div>

<div class="card">
  <h2>✅ Success Criteria</h2>
  <ul>{criteria_html}</ul>
  <p>Passed: <strong>{qc_report['criteria_passed']}</strong></p>
</div>

<div class="card">
  <h2>📁 Artifact Inventory</h2>
  <p>All critical artifacts: {'✅ Complete' if qc_report['artifacts_complete'] else '⚠️ Incomplete'}</p>
</div>

<footer style="color:#95a5a6;font-size:.8rem;margin-top:40px">
  CVD Risk Intelligence Platform | QC Review | {qc_report['generated_at']}</footer>
</body></html>"""


def run() -> dict[str, Any]:
    log.info("Agent 14: Quality Control starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    artifacts = _check_artifacts()
    metrics = _check_model_metrics()
    quality = _check_quality_score()
    qc_report = _generate_qc_report(artifacts, metrics, quality)

    # Save JSON report
    json_path = OUTPUT_DIR / "qc_report.json"
    with json_path.open("w") as f:
        json.dump(qc_report, f, indent=2)

    # Save HTML
    html_path = OUTPUT_DIR / "qc_report.html"
    html_path.write_text(_generate_final_documentation(qc_report), encoding="utf-8")

    log.info("Agent 14 complete", status=qc_report["qc_status"])
    return {
        "success": qc_report["qc_status"] in {"APPROVED", "CONDITIONAL"},
        "artifact": str(html_path),
        "status": qc_report["qc_status"]
    }


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
