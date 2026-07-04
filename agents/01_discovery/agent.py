"""
AGENT 1 — Dataset Discovery Agent
SDD Spec: Locate, profile, and catalog all CVD dataset files.

BDD:
  Feature: Dataset Discovery
  Scenario: Catalog all spreadsheet files
    Given the 'cvd risk dataset' folder exists
    When the agent scans all files
    Then it produces dataset_catalog.json
    And produces data_dictionary.md
    And all column types are inferred
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import structlog

log = structlog.get_logger()

DATASET_DIR = Path("cvd risk dataset")
OUTPUT_DIR = Path("outputs/01_data_catalog")
SUPPORTED_EXT = {".csv", ".xlsx", ".xls", ".parquet", ".json"}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_file(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path, low_memory=False)
    elif ext in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported file type: {ext}")


def _profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {}
    for col in df.columns:
        s = df[col]
        profile[col] = {
            "dtype": str(s.dtype),
            "non_null_count": int(s.notna().sum()),
            "null_count": int(s.isna().sum()),
            "null_pct": round(float(s.isna().mean()) * 100, 2),
            "unique_count": int(s.nunique()),
            "sample_values": s.dropna().head(5).tolist(),
        }
        if pd.api.types.is_numeric_dtype(s):
            desc = s.describe()
            profile[col].update({
                "min": float(desc["min"]),
                "max": float(desc["max"]),
                "mean": round(float(desc["mean"]), 4),
                "std": round(float(desc["std"]), 4),
                "q25": float(desc["25%"]),
                "q75": float(desc["75%"]),
            })
    return profile


def _infer_target_column(df: pd.DataFrame) -> str | None:
    """Heuristically find the CVD target column."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    env_target = os.getenv("PRIMARY_TARGET_COLUMN")
    if env_target and env_target in df.columns:
        return env_target

    candidates = [
        "target", "cvd", "cardio", "heart_disease", "cardiovascular",
        "highrisk", "cvdrisk", "risk", "outcome", "label", "class", "diagnosis"
    ]
    for col in df.columns:
        col_clean = col.lower().strip().replace("_", "")
        if col_clean in candidates:
            return col
    # Check binary columns with small cardinality
    for col in df.columns:
        if df[col].nunique() <= 2:
            return col
    return None


def _generate_data_dictionary(catalog: list[dict]) -> str:
    lines = ["# CVD Risk Dataset — Data Dictionary\n",
             f"_Generated: {datetime.now(timezone.utc).isoformat()}_\n"]
    for entry in catalog:
        lines.append(f"\n## File: `{entry['filename']}`\n")
        lines.append(f"- **Rows:** {entry['rows']:,}  ")
        lines.append(f"- **Columns:** {entry['columns']}  ")
        lines.append(f"- **Target Column:** `{entry.get('target_column', 'Unknown')}`\n")
        lines.append("\n| Column | Type | Null% | Unique | Notes |\n")
        lines.append("|--------|------|-------|--------|-------|\n")
        for col, meta in entry["column_profiles"].items():
            notes = ""
            if meta["null_pct"] > 20:
                notes = "⚠️ High missingness"
            elif meta["null_pct"] > 5:
                notes = "⚡ Moderate missingness"
            lines.append(
                f"| `{col}` | {meta['dtype']} | {meta['null_pct']}% "
                f"| {meta['unique_count']} | {notes} |\n"
            )
    return "".join(lines)


def run() -> dict[str, Any]:
    """Entry point called by orchestrator."""
    log.info("Agent 1: Dataset Discovery starting", dataset_dir=str(DATASET_DIR))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DATASET_DIR.exists():
        log.error("Dataset directory not found", path=str(DATASET_DIR))
        return {"success": False, "artifact": ""}

    catalog: list[dict] = []

    files = [f for f in DATASET_DIR.rglob("*") if f.suffix.lower() in SUPPORTED_EXT]
    log.info("Files found", count=len(files))

    for file_path in files:
        log.info("Profiling file", file=file_path.name)
        try:
            df = _load_file(file_path)
            target_col = _infer_target_column(df)
            profile = _profile_dataframe(df)

            entry = {
                "filename": file_path.name,
                "relative_path": str(file_path),
                "file_size_kb": round(file_path.stat().st_size / 1024, 2),
                "sha256": _sha256_file(file_path),
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "target_column": target_col,
                "class_distribution": (
                    df[target_col].value_counts().to_dict()
                    if target_col else None
                ),
                "column_profiles": profile,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            }
            catalog.append(entry)
            log.info("File profiled", file=file_path.name, rows=len(df), cols=len(df.columns))

        except Exception as exc:
            log.error("Failed to profile file", file=file_path.name, error=str(exc))

    # Write catalog JSON
    catalog_path = OUTPUT_DIR / "dataset_catalog.json"
    with catalog_path.open("w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "total_files": len(catalog),
                   "files": catalog}, f, indent=2, default=str)

    # Write data dictionary Markdown
    dict_path = OUTPUT_DIR / "data_dictionary.md"
    dict_path.write_text(_generate_data_dictionary(catalog), encoding="utf-8")

    log.info("Agent 1 complete", catalog=str(catalog_path), dictionary=str(dict_path))
    return {"success": True, "artifact": str(catalog_path)}


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2))
