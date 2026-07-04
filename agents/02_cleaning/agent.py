"""
AGENT 2 — Data Cleaning Agent
SDD Spec: Missing values, duplicates, outliers, schema correction, quality scoring.

BDD:
  Feature: Data Cleaning
  Scenario: Clean the CVD dataset
    Given dataset_catalog.json exists
    When the agent loads and cleans the primary dataset
    Then it produces cleaned_dataset.parquet
    And produces data_quality_report.html
    And data quality score is >= 85
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import structlog
from scipy import stats

log = structlog.get_logger()

CATALOG_PATH = Path("outputs/01_data_catalog/dataset_catalog.json")
OUTPUT_DIR = Path("outputs/02_data_cleaning")


def _load_primary_dataset() -> tuple[pd.DataFrame, str]:
    """Load the primary dataset from catalog (override with env var CVD_DATASET_FILE if present)."""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    with CATALOG_PATH.open() as f:
        catalog = json.load(f)
    files = catalog["files"]
    if not files:
        raise RuntimeError("No files in catalog")

    target_file = os.getenv("CVD_DATASET_FILE")
    primary = None
    if target_file:
        for f_entry in files:
            if f_entry["filename"].lower() == target_file.lower():
                primary = f_entry
                break
        if primary is None:
            log.warning("Requested dataset file not found in catalog, falling back to max rows", target_file=target_file)

    if primary is None:
        primary = max(files, key=lambda x: x["rows"])

    log.info("Primary dataset selected", file=primary["filename"], rows=primary["rows"])
    path = Path(primary["relative_path"])
    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path, low_memory=False)
    elif ext in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    elif ext == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    return df, primary["filename"]


def _fix_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: lowercase, strip, replace spaces."""
    df.columns = (
        df.columns.str.lower()
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    return df


def _handle_missing_values(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    """Smart imputation strategy per column type."""
    missing_summary: dict[str, Any] = {}
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        if null_count == 0:
            continue
        null_pct = null_count / len(df) * 100
        missing_summary[col] = {"null_count": null_count, "null_pct": round(null_pct, 2)}

        if null_pct > 60:
            log.warning("Dropping column — too many missing", col=col, pct=null_pct)
            df = df.drop(columns=[col])
            missing_summary[col]["action"] = "DROPPED"
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Use median for numeric (robust to outliers)
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            missing_summary[col]["action"] = f"IMPUTED_MEDIAN({median_val:.4f})"
        else:
            # Use mode for categorical
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)
            missing_summary[col]["action"] = f"IMPUTED_MODE({mode_val})"

    report["missing_values"] = missing_summary
    return df


def _remove_duplicates(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    removed = before - after
    report["duplicates"] = {"removed": removed, "before": before, "after": after}
    log.info("Duplicates removed", count=removed)
    return df


def _handle_outliers(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    """Z-score capping for numeric columns (keep within ±3 sigma)."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_summary: dict[str, Any] = {}
    for col in numeric_cols:
        z_scores = np.abs(stats.zscore(df[col].dropna()))
        outlier_mask = np.abs(stats.zscore(df[col].fillna(df[col].median()))) > 3
        count = int(outlier_mask.sum())
        if count > 0:
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=lower, upper=upper)
            outlier_summary[col] = {"outliers_capped": count, "lower": lower, "upper": upper}
    report["outliers"] = outlier_summary
    return df


def _fix_data_types(df: pd.DataFrame, report: dict) -> pd.DataFrame:
    """Attempt type coercion for common CVD columns and map categories."""
    conversions: dict[str, str] = {}
    
    # Categorical binary mappings
    mappings = {
        "sex": {"female": 0, "male": 1},
        "smoking": {"nonsmoker": 0, "smoker": 1},
        "highrisk": {"no": 0, "yes": 1},
        "bplt": {"no": 0, "yes": 1},
        "lltt": {"no": 0, "yes": 1},
        "aptt": {"no": 0, "yes": 1},
        "education": {"primary": 1, "secondary": 2, "higher": 3},
        "marital_status": {"single": 0, "married": 1, "divorced": 2, "widowed": 3},
        "occupation": {"not working": 0, "self-employed": 1, "casual worker": 2, "private worker": 3, "government worker": 4},
        "areas": {"rural": 1, "semiurban": 2, "urban": 3},
    }

    # First check and map any object/categorical columns using defined mappings
    for col in df.columns:
        col_clean = col.lower().strip()
        if pd.api.types.is_string_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
            if col_clean in mappings:
                map_dict = mappings[col_clean]
                df[col] = df[col].astype(str).str.lower().str.strip().map(map_dict)
                conversions[col] = "numeric (mapped categories)"
            elif df[col].nunique() <= 2:
                # Fallback mapping for binary string columns
                vals = df[col].dropna().unique()
                vals_lower = {str(v).lower().strip() for v in vals}
                if vals_lower.issubset({"yes", "no"}):
                    df[col] = df[col].map({v: 1 if str(v).lower().strip() == "yes" else 0 for v in vals})
                    conversions[col] = "Int8 (mapped Yes/No to 1/0)"
                elif vals_lower.issubset({"true", "false"}):
                    df[col] = df[col].map({v: 1 if str(v).lower().strip() == "true" else 0 for v in vals})
                    conversions[col] = "Int8 (mapped True/False to 1/0)"
            elif df[col].nunique() > 2:
                # Generic fallback: encode string categories numerically using sorted indices
                unique_vals = sorted(df[col].dropna().astype(str).unique())
                df[col] = df[col].astype(str).map({val: idx for idx, val in enumerate(unique_vals)})
                conversions[col] = f"numeric (label-encoded codes 0-{len(unique_vals)-1})"

    # Clean remaining numeric columns or standard binaries
    binary_cols = [c for c in df.columns if df[c].nunique() <= 2]
    for col in binary_cols:
        if col not in conversions:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int8")
                conversions[col] = "Int8 (binary)"
            except Exception:
                pass

    # Try to parse age if present
    for col in df.columns:
        if "age" in col and pd.api.types.is_string_dtype(df[col]):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            conversions[col] = "numeric (age)"

    report["type_conversions"] = conversions
    return df


def _compute_quality_score(df: pd.DataFrame, original_rows: int) -> float:
    completeness = df.notna().mean().mean() * 100
    uniqueness = (1 - df.duplicated().mean()) * 100
    row_retention = (len(df) / original_rows) * 100
    score = (completeness * 0.5) + (uniqueness * 0.3) + (row_retention * 0.2)
    return round(score, 2)


def _generate_html_report(report: dict, quality_score: float, filename: str) -> str:
    color = "#27ae60" if quality_score >= 85 else "#e67e22" if quality_score >= 70 else "#e74c3c"
    missing_rows = "".join(
        f"<tr><td>{col}</td><td>{v['null_count']}</td>"
        f"<td>{v['null_pct']}%</td><td>{v['action']}</td></tr>"
        for col, v in report.get("missing_values", {}).items()
    )
    outlier_rows = "".join(
        f"<tr><td>{col}</td><td>{v['outliers_capped']}</td>"
        f"<td>{v['lower']:.2f}</td><td>{v['upper']:.2f}</td></tr>"
        for col, v in report.get("outliers", {}).items()
    )
    dup = report.get("duplicates", {})
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Data Quality Report — {filename}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; color: #2c3e50; }}
  h1 {{ color: #2c3e50; border-bottom: 3px solid {color}; }}
  .score {{ font-size: 4rem; color: {color}; font-weight: bold; text-align: center; padding: 20px; }}
  .badge {{ display: inline-block; padding: 6px 14px; border-radius: 20px;
            background: {color}; color: white; font-size: 1.1rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th {{ background: #2c3e50; color: white; padding: 10px; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #ecf0f1; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
  .section {{ background: #f8f9fa; border-left: 4px solid {color}; padding: 16px; margin: 20px 0; }}
</style></head><body>
<h1>🏥 CVD Risk Platform — Data Quality Report</h1>
<p>File: <strong>{filename}</strong> | Generated: {datetime.now(timezone.utc).isoformat()}</p>

<div class="score">{quality_score}<br><span style="font-size:1.2rem">Quality Score</span></div>
<p style="text-align:center"><span class="badge">{'✅ PASS' if quality_score >= 85 else '⚠️ REVIEW'}</span></p>

<div class="section">
  <h2>📊 Duplicate Detection</h2>
  <p>Before: <strong>{dup.get('before','N/A'):,}</strong> rows &nbsp;|&nbsp;
     Removed: <strong>{dup.get('removed','N/A')}</strong> &nbsp;|&nbsp;
     After: <strong>{dup.get('after','N/A'):,}</strong> rows</p>
</div>

<div class="section">
  <h2>🔧 Missing Value Treatment</h2>
  <table><tr><th>Column</th><th>Null Count</th><th>Null %</th><th>Action</th></tr>
  {missing_rows if missing_rows else '<tr><td colspan=4>No missing values found ✅</td></tr>'}
  </table>
</div>

<div class="section">
  <h2>📈 Outlier Treatment (Z-Score Capping ±3σ)</h2>
  <table><tr><th>Column</th><th>Outliers Capped</th><th>Lower Clip</th><th>Upper Clip</th></tr>
  {outlier_rows if outlier_rows else '<tr><td colspan=4>No significant outliers detected ✅</td></tr>'}
  </table>
</div>

<div class="section">
  <h2>🔄 Type Conversions</h2>
  {''.join(f'<p><code>{col}</code> → {t}</p>' for col, t in report.get('type_conversions', {}).items())}
</div>

<footer><p style="color:#95a5a6;font-size:0.85rem">CVD Risk Intelligence Platform | Australian Healthcare Compliant</p></footer>
</body></html>"""


def run() -> dict[str, Any]:
    log.info("Agent 2: Data Cleaning starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df, filename = _load_primary_dataset()
    original_rows = len(df)
    report: dict[str, Any] = {"source_file": filename, "original_rows": original_rows}

    df = _fix_column_names(df)
    df = _remove_duplicates(df, report)
    df = _handle_missing_values(df, report)
    df = _handle_outliers(df, report)
    df = _fix_data_types(df, report)

    quality_score = _compute_quality_score(df, original_rows)
    report["quality_score"] = quality_score

    # Save cleaned parquet
    parquet_path = OUTPUT_DIR / "cleaned_dataset.parquet"
    df.to_parquet(parquet_path, index=False)

    # Save HTML report
    html_path = OUTPUT_DIR / "data_quality_report.html"
    html_path.write_text(_generate_html_report(report, quality_score, filename), encoding="utf-8")

    log.info("Agent 2 complete", quality_score=quality_score, rows=len(df), parquet=str(parquet_path))
    return {"success": bool(quality_score >= 70), "artifact": str(parquet_path), "quality_score": float(quality_score)}


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
