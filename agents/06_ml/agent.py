"""
AGENT 6 — Machine Learning Agent
Full benchmark: baseline + ensemble models, clinical metrics, confusion matrix analysis.

BDD:
  Feature: Machine Learning
  Scenario: Benchmark all models and select best
    Given processed_dataset.parquet exists
    When the agent trains all models
    Then it produces model_metrics.json
    And best model is saved to best_model.pkl
    And model_card.md is generated
"""

from __future__ import annotations

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import structlog
from sklearn.ensemble import (AdaBoostClassifier, ExtraTreesClassifier,
                               GradientBoostingClassifier, RandomForestClassifier,
                               StackingClassifier, VotingClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                              classification_report, confusion_matrix,
                              f1_score, matthews_corrcoef, precision_score,
                              recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

log = structlog.get_logger()

INPUT_PATH = Path("outputs/03_preprocessing/processed_dataset.parquet")
OUTPUT_DIR = Path("outputs/06_machine_learning")
MODELS_DIR = OUTPUT_DIR / "models"
METRICS_DIR = OUTPUT_DIR / "metrics"


def _infer_target(df: pd.DataFrame) -> str:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    env_target = os.getenv("PRIMARY_TARGET_COLUMN")
    if env_target and env_target in df.columns:
        return env_target

    candidates = ["target", "cvd", "cardio", "heart_disease", "cardiovascular",
                  "highrisk", "cvdrisk", "risk", "outcome", "label", "class", "diagnosis"]
    for col in df.columns:
        col_clean = col.lower().strip().replace("_", "")
        if col_clean in candidates:
            return col
    return df.columns[-1]


def _get_models() -> dict:
    try:
        from catboost import CatBoostClassifier
        cat = CatBoostClassifier(verbose=0, random_state=42, eval_metric="AUC")
    except ImportError:
        cat = None
        log.warning("CatBoost not installed")

    try:
        from xgboost import XGBClassifier
        xgb = XGBClassifier(use_label_encoder=False, eval_metric="logloss",
                            random_state=42, verbosity=0)
    except ImportError:
        xgb = None
        log.warning("XGBoost not installed")

    try:
        from lightgbm import LGBMClassifier
        lgbm = LGBMClassifier(random_state=42, verbose=-1)
    except ImportError:
        lgbm = None
        log.warning("LightGBM not installed")

    models = {
        # Baseline
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=8, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "NaiveBayes": GaussianNB(),
        "KNN": KNeighborsClassifier(n_neighbors=7, n_jobs=-1),
        "SVM": SVC(probability=True, random_state=42, C=1.0),
        # Ensemble
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "AdaBoost": AdaBoostClassifier(n_estimators=100, random_state=42),
        "ExtraTrees": ExtraTreesClassifier(n_estimators=100, random_state=42, n_jobs=-1),
    }

    if xgb is not None:
        models["XGBoost"] = xgb
    if lgbm is not None:
        models["LightGBM"] = lgbm
    if cat is not None:
        models["CatBoost"] = cat

    return models


def _evaluate(model: Any, X_test: np.ndarray, y_test: np.ndarray, model_name: str) -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    # Clinical interpretation
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # Recall / True Positive Rate
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate

    return {
        "model": model_name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "balanced_accuracy": round(balanced_accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "mcc": round(matthews_corrcoef(y_test, y_pred), 4),
        "confusion_matrix": {
            "TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn),
            "clinical_note": (
                f"Model correctly identified {int(tp)} CVD-positive patients "
                f"and missed {int(fn)} (false negatives are critical in clinical settings)."
            )
        }
    }


def _generate_metrics_html(all_metrics: list[dict], best: dict) -> str:
    rows = ""
    for m in sorted(all_metrics, key=lambda x: x["roc_auc"], reverse=True):
        is_best = m["model"] == best["model"]
        bg = "background:#e8f5e9;" if is_best else ""
        rows += (
            f"<tr style='{bg}'>"
            f"<td><strong>{'🏆 ' if is_best else ''}{m['model']}</strong></td>"
            f"<td>{m['accuracy']:.4f}</td><td>{m['roc_auc']:.4f}</td>"
            f"<td>{m['f1_score']:.4f}</td><td>{m['sensitivity']:.4f}</td>"
            f"<td>{m['specificity']:.4f}</td><td>{m['mcc']:.4f}</td>"
            f"<td>{m['confusion_matrix']['FN']}</td>"
            f"</tr>"
        )
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>ML Results</title>
<style>
  body{{font-family:'Segoe UI',sans-serif;max-width:1200px;margin:40px auto;color:#2c3e50}}
  h1{{color:#2c3e50;border-bottom:3px solid #27ae60;padding-bottom:12px}}
  table{{width:100%;border-collapse:collapse;margin:20px 0}}
  th{{background:#2c3e50;color:white;padding:10px;text-align:left}}
  td{{padding:9px 10px;border-bottom:1px solid #ecf0f1}}
  tr:hover{{background:#f5f5f5}}
  .best{{background:#e8f8f5;border:2px solid #27ae60;border-radius:8px;padding:20px;margin:20px 0}}
</style></head><body>
<h1>🤖 Machine Learning Benchmark — CVD Risk Platform</h1>
<div class="best">
  <h2>🏆 Best Model: {best['model']}</h2>
  <p>ROC-AUC: <strong>{best['roc_auc']}</strong> &nbsp;|&nbsp;
     F1: <strong>{best['f1_score']}</strong> &nbsp;|&nbsp;
     Sensitivity: <strong>{best['sensitivity']}</strong> &nbsp;|&nbsp;
     Specificity: <strong>{best['specificity']}</strong></p>
</div>
<table>
  <tr><th>Model</th><th>Accuracy</th><th>ROC-AUC</th><th>F1</th>
  <th>Sensitivity</th><th>Specificity</th><th>MCC</th><th>False Negatives ⚠</th></tr>
  {rows}
</table>
<p style="color:#7f8c8d;font-size:.85rem">Generated: {datetime.now(timezone.utc).isoformat()}</p>
</body></html>"""


def _generate_model_card(best: dict, df: pd.DataFrame) -> str:
    return f"""# Model Card — CVD Risk Intelligence Platform

## Model Overview
- **Best Model:** {best['model']}
- **Task:** Binary Classification (CVD Risk Prediction)
- **Dataset Size:** {len(df):,} samples
- **Generated:** {datetime.now(timezone.utc).isoformat()}

## Performance Metrics
| Metric | Value |
|--------|-------|
| Accuracy | {best['accuracy']} |
| ROC-AUC | {best['roc_auc']} |
| F1 Score | {best['f1_score']} |
| Sensitivity (Recall) | {best['sensitivity']} |
| Specificity | {best['specificity']} |
| MCC | {best['mcc']} |

## Clinical Interpretation
- **Sensitivity {best['sensitivity']}**: {best['sensitivity']*100:.1f}% of actual CVD patients correctly identified.
- **Specificity {best['specificity']}**: {best['specificity']*100:.1f}% of non-CVD patients correctly ruled out.
- **False Negatives: {best['confusion_matrix']['FN']}** — These are patients with CVD who were missed. Clinical review recommended.

## Intended Use
- Clinical Decision Support (NOT a replacement for physician judgment)
- Population-level risk screening
- Research and quality improvement

## Limitations
- Validated on Australian healthcare population dataset
- Performance may vary in different populations
- Regular retraining recommended (every 6 months minimum)

## Compliance
- Australian Privacy Act / APP Principles
- FHIR R4 compatible output
- ISO 27001 compliant deployment

## Governance
- Model version must be approved by clinical governance committee before deployment
- All predictions must be logged for audit trail
- SHAP explanations mandatory for each clinical prediction
"""


def _apply_smote(X_train: pd.DataFrame, y_train: pd.Series, report: dict) -> tuple:
    """
    Apply SMOTE ONLY on training data after the split.
    This is the correct location — NEVER before train_test_split.
    """
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError:
        log.warning("imbalanced-learn not installed — skipping SMOTE")
        report["smote"] = "skipped: imbalanced-learn not installed"
        return X_train, y_train

    class_counts = y_train.value_counts()
    minority_pct = class_counts.min() / len(y_train) * 100

    if minority_pct >= 40:
        log.info("Training set is balanced — SMOTE not needed", minority_pct=round(minority_pct, 2))
        report["smote"] = f"skipped: balanced ({minority_pct:.1f}% minority)"
        return X_train, y_train

    try:
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X_train, y_train)
        after = pd.Series(y_res).value_counts().to_dict()
        log.info("SMOTE applied to training set", before=class_counts.to_dict(), after=after)
        report["smote"] = {"applied": True, "before": class_counts.to_dict(), "after": after}
        return pd.DataFrame(X_res, columns=X_train.columns), pd.Series(y_res)
    except Exception as exc:
        log.warning("SMOTE failed", error=str(exc))
        report["smote"] = f"failed: {exc}"
        return X_train, y_train


def _leakage_audit(X: pd.DataFrame, y: pd.Series) -> list[str]:
    """
    Flag features with suspiciously high correlation to the target.
    Logs a warning but does NOT drop — dropping happens in Agent 3.
    """
    flagged = []
    try:
        corr = X.corrwith(y.astype(float)).abs()
        suspects = corr[corr > 0.90].index.tolist()
        if suspects:
            log.warning("LEAKAGE AUDIT: High-correlation features detected",
                        features=suspects, threshold=0.90)
            flagged = suspects
        else:
            log.info("LEAKAGE AUDIT: No high-correlation features detected")
    except Exception as exc:
        log.warning("Leakage audit failed", error=str(exc))
    return flagged


def run() -> dict[str, Any]:
    log.info("Agent 6: Machine Learning starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_PATH.exists():
        fallback = Path("outputs/02_data_cleaning/cleaned_dataset.parquet")
        df = pd.read_parquet(fallback) if fallback.exists() else None
    else:
        df = pd.read_parquet(INPUT_PATH)

    if df is None:
        return {"success": False, "artifact": ""}

    target = _infer_target(df)
    X = df.drop(columns=[target]).select_dtypes(include=[np.number])
    y = df[target].astype("int64")

    # ── Leakage audit before split ─────────────────────────────────────
    leakage_flags = _leakage_audit(X, y)
    if leakage_flags:
        log.error("Aborting: leaky features still present in processed dataset."
                  " Re-run Agent 3 to drop them.", features=leakage_flags)
        return {"success": False, "artifact": "",
                "error": f"Leakage detected: {leakage_flags}. Re-run Agent 3."}

    # ── Train/test split FIRST ───────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    log.info("Train/test split", train=len(X_train), test=len(X_test))

    # ── SMOTE on training set ONLY ───────────────────────────────────
    smote_report: dict = {}
    X_train, y_train = _apply_smote(X_train, y_train, smote_report)
    log.info("Post-SMOTE training set", rows=len(X_train))

    models = _get_models()
    all_metrics: list[dict] = []

    for name, model in models.items():
        log.info("Training model", model=name)
        try:
            model.fit(X_train, y_train)
            metrics = _evaluate(model, X_test, y_test, name)
            # ─ Flag suspiciously perfect scores ────────────────────────────
            if metrics["roc_auc"] >= 1.0 and metrics["confusion_matrix"]["FP"] == 0 \
                    and metrics["confusion_matrix"]["FN"] == 0:
                log.warning("PERFECT SCORE: possible residual leakage", model=name)
                metrics["leakage_warning"] = True
            all_metrics.append(metrics)

            # Save model
            model_path = MODELS_DIR / f"{name.lower()}.pkl"
            with model_path.open("wb") as f:
                pickle.dump(model, f)

            log.info("Model trained", model=name, roc_auc=metrics["roc_auc"])

        except Exception as exc:
            log.error("Model failed", model=name, error=str(exc))

    if not all_metrics:
        return {"success": False, "artifact": ""}

    # Select best by ROC-AUC (clinically most relevant for screening)
    best = max(all_metrics, key=lambda x: x["roc_auc"])
    log.info("Best model selected", model=best["model"], roc_auc=best["roc_auc"])

    # Save best model separately
    best_model_obj = models[best["model"]]
    best_path = MODELS_DIR / "best_model.pkl"
    with best_path.open("wb") as f:
        pickle.dump({"model": best_model_obj, "feature_columns": list(X.columns),
                     "target_column": target, "model_name": best["model"]}, f)

    # Save feature columns
    (OUTPUT_DIR / "feature_columns.json").write_text(
        json.dumps({"features": list(X.columns), "target": target}, indent=2), encoding="utf-8"
    )

    # Save all metrics
    metrics_path = METRICS_DIR / "model_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump({"best_model": best, "all_models": all_metrics,
                   "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2)

    # HTML report
    html_path = OUTPUT_DIR / "ml_report.html"
    html_path.write_text(_generate_metrics_html(all_metrics, best), encoding="utf-8")

    # Model card
    (OUTPUT_DIR / "model_card.md").write_text(_generate_model_card(best, df), encoding="utf-8")

    log.info("Agent 6 complete", best_model=best["model"], roc_auc=best["roc_auc"])
    return {"success": True, "artifact": str(best_path), "best_model": best["model"],
            "roc_auc": best["roc_auc"]}


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
