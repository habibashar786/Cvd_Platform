"""
AGENT 3 — Data Preprocessing Agent
Normalization, encoding, feature engineering + imbalanced learning.

BDD:
  Feature: Data Preprocessing
  Scenario: Preprocess cleaned CVD dataset
    Given cleaned_dataset.parquet exists
    When the agent applies transformations
    Then it produces processed_dataset.parquet
    And it resolves class imbalance
    And scalers are saved for inference
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
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler

log = structlog.get_logger()

INPUT_PATH = Path("outputs/02_data_cleaning/cleaned_dataset.parquet")
OUTPUT_DIR = Path("outputs/03_preprocessing")

# CVD domain: columns that should be binary-encoded
BINARY_THRESHOLD = 3

# ── Leakage blocklist ────────────────────────────────────────────────────────
# Columns that encode or directly derive the target must NEVER enter the feature
# matrix. Extend this list if your dataset has other derived risk columns.
LEAKY_COLUMNS: list[str] = [
    "cvdrisk",          # pre-computed composite risk score → encodes 'highrisk'
    "patient_id",       # identifier with no predictive value
]
# Any column whose lowered name contains these substrings is also dropped.
LEAKY_SUBSTRINGS: list[str] = ["risk_score", "risk_label", "risk_prob", "prediction"]


def _load_cleaned() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Cleaned dataset not found: {INPUT_PATH}")
    return pd.read_parquet(INPUT_PATH)


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
    # Fallback: last column if binary
    last = df.columns[-1]
    if df[last].nunique() <= 2:
        return last
    raise ValueError("Cannot infer target column. Check dataset.")


def _encode_categoricals(df: pd.DataFrame, target: str, report: dict) -> pd.DataFrame:
    encodings: dict[str, str] = {}
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    cat_cols = [c for c in cat_cols if c != target]

    for col in cat_cols:
        n_unique = df[col].nunique()
        if n_unique <= BINARY_THRESHOLD:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encodings[col] = f"LabelEncoder ({n_unique} classes)"
        else:
            # One-hot for nominal with moderate cardinality
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            encodings[col] = f"OneHot ({n_unique} classes → {len(dummies.columns)} dummies)"

    report["categorical_encoding"] = encodings
    return df


def _scale_features(df: pd.DataFrame, target: str, report: dict) -> tuple[pd.DataFrame, dict]:
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c != target]

    scalers: dict[str, Any] = {}

    # RobustScaler for clinical measurements (handles outliers better)
    clinical_cols = [c for c in num_cols if any(
        kw in c for kw in ["bp", "pressure", "chol", "glucose", "gluc", "bmi", "weight", "height"]
    )]
    standard_cols = [c for c in num_cols if c not in clinical_cols]

    if clinical_cols:
        rs = RobustScaler()
        df[clinical_cols] = rs.fit_transform(df[clinical_cols])
        scalers["RobustScaler"] = {"scaler": rs, "columns": clinical_cols}
        report["scaling"] = report.get("scaling", {})
        report["scaling"]["RobustScaler"] = clinical_cols

    if standard_cols:
        ss = StandardScaler()
        df[standard_cols] = ss.fit_transform(df[standard_cols])
        scalers["StandardScaler"] = {"scaler": ss, "columns": standard_cols}
        report["scaling"] = report.get("scaling", {})
        report["scaling"]["StandardScaler"] = standard_cols

    return df, scalers


def _drop_leaky_columns(df: pd.DataFrame, target: str, report: dict) -> pd.DataFrame:
    """
    Drop columns that directly or indirectly encode the target.
    This is the primary guard against data leakage.
    """
    to_drop: list[str] = []

    # Explicit blocklist
    for col in LEAKY_COLUMNS:
        if col in df.columns and col != target:
            to_drop.append(col)

    # Substring blocklist
    for col in df.columns:
        if col == target:
            continue
        col_lower = col.lower()
        if any(sub in col_lower for sub in LEAKY_SUBSTRINGS):
            to_drop.append(col)

    # Correlation guard: drop numeric features correlated > 0.95 with target
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    num_cols = [c for c in num_cols if c != target and c not in to_drop]
    try:
        target_corr = df[num_cols].corrwith(df[target].astype(float)).abs()
        high_corr = target_corr[target_corr > 0.95].index.tolist()
        for col in high_corr:
            if col not in to_drop:
                to_drop.append(col)
                log.warning("High-correlation leakage detected", column=col,
                            corr=round(float(target_corr[col]), 4))
    except Exception as exc:
        log.warning("Correlation guard skipped", error=str(exc))

    to_drop = list(dict.fromkeys(to_drop))  # deduplicate, preserve order
    if to_drop:
        df = df.drop(columns=to_drop)
        log.info("Leaky columns removed", dropped=to_drop)
    else:
        log.info("No leaky columns detected")

    report["leakage_audit"] = {
        "dropped_columns": to_drop,
        "reason": "Columns encode or strongly correlate with target",
    }
    return df


def _note_imbalance(df: pd.DataFrame, target: str, report: dict) -> None:
    """
    Record class distribution for the report.
    SMOTE is intentionally NOT applied here — it must run inside Agent 6
    AFTER train_test_split() so synthetic samples never contaminate the test set.
    """
    y = df[target].astype("int64")
    class_counts = y.value_counts()
    minority_pct = class_counts.min() / len(y) * 100
    report["imbalance"] = {
        "original_distribution": class_counts.to_dict(),
        "minority_pct": round(minority_pct, 2),
        "strategy": "SMOTE applied in Agent 6 after train/test split (leakage-safe)",
    }
    log.info("Class distribution noted", minority_pct=round(minority_pct, 2))


def _feature_engineering(df: pd.DataFrame, target: str, report: dict) -> pd.DataFrame:
    """Create domain-specific CVD features if base columns exist."""
    engineered: list[str] = []
    cols = set(df.columns)

    # Pulse pressure = systolic - diastolic
    if {"ap_hi", "ap_lo"}.issubset(cols):
        df["pulse_pressure"] = df["ap_hi"] - df["ap_lo"]
        engineered.append("pulse_pressure")

    # BMI = weight(kg) / height(m)^2
    if {"weight", "height"}.issubset(cols):
        height_m = df["height"] / 100 if df["height"].mean() > 10 else df["height"]
        df["bmi"] = df["weight"] / (height_m ** 2)
        engineered.append("bmi")

    # Age in decades (clinical grouping)
    if "age" in cols:
        df["age_decade"] = (df["age"] // 10).astype(int)
        engineered.append("age_decade")

    report["feature_engineering"] = engineered
    return df


def run() -> dict[str, Any]:
    log.info("Agent 3: Preprocessing starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {}

    df = _load_cleaned()
    target = _infer_target(df)
    log.info("Target column identified", target=target)

    df = _drop_leaky_columns(df, target, report)   # ← must be FIRST
    df = _feature_engineering(df, target, report)
    df = _encode_categoricals(df, target, report)
    df, scalers = _scale_features(df, target, report)
    _note_imbalance(df, target, report)              # record only, no SMOTE here

    # Save processed dataset
    out_path = OUTPUT_DIR / "processed_dataset.parquet"
    df.to_parquet(out_path, index=False)

    # Save scalers
    scalers_path = OUTPUT_DIR / "scalers.pkl"
    with scalers_path.open("wb") as f:
        pickle.dump(scalers, f)

    # Save metadata
    meta_path = OUTPUT_DIR / "preprocessing_report.json"
    report["target_column"] = target
    report["output_shape"] = {"rows": len(df), "cols": len(df.columns)}
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    with meta_path.open("w") as f:
        json.dump(report, f, indent=2, default=lambda x: int(x) if hasattr(x,"item") else str(x))

    log.info("Agent 3 complete", rows=len(df), cols=len(df.columns), output=str(out_path))
    return {"success": True, "artifact": str(out_path)}


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
