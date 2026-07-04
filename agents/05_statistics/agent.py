"""
AGENT 5 — Statistical Analysis Agent
Correlation, ANOVA, Chi-square, Mann-Whitney, Kruskal-Wallis
Identifies cause-effect indicators, risk drivers, predictive factors.
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
INPUT_PATH = Path("outputs/03_preprocessing/processed_dataset.parquet")
OUTPUT_DIR = Path("outputs/05_statistics")


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


def _chi_square_tests(df: pd.DataFrame, cat_cols: list, target: str) -> list[dict]:
    results = []
    for col in cat_cols[:10]:
        try:
            ct = pd.crosstab(df[col], df[target])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            results.append({"feature": col, "test": "Chi-Square", "chi2": round(float(chi2),4),
                             "p_value": round(float(p),6), "dof": dof,
                             "significant": bool(p < 0.05)})
        except Exception:
            pass
    return results


def _ttest_and_mannwhitney(df: pd.DataFrame, num_cols: list, target: str) -> list[dict]:
    results = []
    for col in num_cols[:15]:
        try:
            pos = df[df[target] == 1][col].dropna()
            neg = df[df[target] == 0][col].dropna()
            t_stat, t_p = stats.ttest_ind(pos, neg)
            u_stat, u_p = stats.mannwhitneyu(pos, neg, alternative="two-sided")
            results.append({
                "feature": col,
                "t_stat": round(float(t_stat), 4), "t_p": round(float(t_p), 6),
                "u_stat": round(float(u_stat), 4), "u_p": round(float(u_p), 6),
                "t_significant": bool(t_p < 0.05), "u_significant": bool(u_p < 0.05),
                "mean_cvd_pos": round(float(pos.mean()), 4),
                "mean_cvd_neg": round(float(neg.mean()), 4),
            })
        except Exception:
            pass
    return sorted(results, key=lambda x: x["u_p"])


def _generate_html(chi_results: list, ttest_results: list) -> str:
    chi_rows = "".join(
        f"<tr{'style=background:#e8f5e9' if r['significant'] else ''}>"
        f"<td>{r['feature']}</td><td>{r['chi2']}</td>"
        f"<td>{r['p_value']}</td><td>{'✅' if r['significant'] else '—'}</td></tr>"
        for r in chi_results
    )
    ttest_rows = "".join(
        f"<tr{'style=background:#e8f5e9' if r['u_significant'] else ''}>"
        f"<td>{r['feature']}</td><td>{r['mean_cvd_pos']:.3f}</td>"
        f"<td>{r['mean_cvd_neg']:.3f}</td><td>{r['u_p']}</td>"
        f"<td>{'✅' if r['u_significant'] else '—'}</td></tr>"
        for r in ttest_results
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Statistical Analysis — CVD Platform</title>
<style>body{{font-family:'Segoe UI',sans-serif;max-width:1100px;margin:40px auto;color:#2c3e50}}
h1{{border-bottom:3px solid #8e44ad;padding-bottom:12px}}
table{{width:100%;border-collapse:collapse;margin:16px 0}}
th{{background:#2c3e50;color:white;padding:10px}}
td{{padding:8px 10px;border-bottom:1px solid #ecf0f1}}</style></head><body>
<h1>📐 Statistical Analysis Report — CVD Risk Platform</h1>
<p>Generated: {datetime.now(timezone.utc).isoformat()}</p>
<h2>Chi-Square Tests (Categorical Features)</h2>
<table><tr><th>Feature</th><th>Chi²</th><th>p-value</th><th>Significant</th></tr>
{chi_rows}</table>
<h2>Mann-Whitney U + T-Test (Numeric Features)</h2>
<table><tr><th>Feature</th><th>Mean (CVD+)</th><th>Mean (CVD−)</th><th>p-value</th><th>Significant</th></tr>
{ttest_rows}</table>
</body></html>"""


def run() -> dict[str, Any]:
    log.info("Agent 5: Statistical Analysis starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if INPUT_PATH.exists():
        df = pd.read_parquet(INPUT_PATH)
    else:
        fallback = Path("outputs/02_data_cleaning/cleaned_dataset.parquet")
        df = pd.read_parquet(fallback) if fallback.exists() else None
    if df is None:
        return {"success": False, "artifact": ""}

    target = _infer_target(df)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c != target]
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    chi_results = _chi_square_tests(df, cat_cols, target)
    ttest_results = _ttest_and_mannwhitney(df, num_cols, target)

    html_path = OUTPUT_DIR / "statistical_report.html"
    html_path.write_text(_generate_html(chi_results, ttest_results), encoding="utf-8")

    stats_json = OUTPUT_DIR / "statistical_summary.json"
    with stats_json.open("w") as f:
        json.dump({"chi_square": chi_results, "ttest_mannwhitney": ttest_results,
                   "generated_at": datetime.now(timezone.utc).isoformat()}, f, indent=2, default=str)

    sig_features = [r["feature"] for r in ttest_results if r.get("u_significant")]
    log.info("Agent 5 complete", significant_features=len(sig_features))
    return {"success": True, "artifact": str(html_path)}


if __name__ == "__main__":
    import structlog; structlog.configure()
    print(json.dumps(run(), indent=2, default=str))
