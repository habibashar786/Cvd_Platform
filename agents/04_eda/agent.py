"""
AGENT 4 — EDA Agent
Publication-quality visualizations: distribution, correlation, clinical insights.

BDD:
  Feature: Exploratory Data Analysis
  Scenario: Generate comprehensive EDA report
    Given processed_dataset.parquet exists
    When the agent performs EDA
    Then it produces eda_report.html
    And all mandatory visualization categories are present
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import structlog

log = structlog.get_logger()

INPUT_PATH = Path("outputs/03_preprocessing/processed_dataset.parquet")
OUTPUT_DIR = Path("outputs/04_eda")


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
    for col in df.columns:
        if df[col].nunique() <= 2:
            return col
    return df.columns[-1]


def _generate_plotly_charts(df: pd.DataFrame, target: str) -> list[str]:
    """Generate Plotly.js chart configs as JSON strings."""
    charts = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in num_cols if c != target]

    # 1. Target distribution
    vc = df[target].value_counts()
    charts.append({
        "title": "Target Class Distribution",
        "type": "pie",
        "data": [{"type": "pie", "labels": [str(k) for k in vc.index],
                  "values": vc.values.tolist(), "hole": 0.4}],
        "layout": {"title": "CVD Risk Class Distribution"}
    })

    # 2. Histograms for top features
    for col in feature_cols[:6]:
        pos = df[df[target] == 1][col].dropna().tolist()
        neg = df[df[target] == 0][col].dropna().tolist()
        charts.append({
            "title": f"Distribution: {col}",
            "type": "histogram",
            "data": [
                {"type": "histogram", "x": pos[:2000], "name": "CVD+", "opacity": 0.7,
                 "marker": {"color": "#e74c3c"}},
                {"type": "histogram", "x": neg[:2000], "name": "CVD−", "opacity": 0.7,
                 "marker": {"color": "#3498db"}}
            ],
            "layout": {"barmode": "overlay", "title": f"Distribution of {col} by CVD Status"}
        })

    # 3. Correlation heatmap
    corr = df[feature_cols[:15]].corr().round(2)
    charts.append({
        "title": "Correlation Heatmap",
        "type": "heatmap",
        "data": [{
            "type": "heatmap",
            "z": corr.values.tolist(),
            "x": corr.columns.tolist(),
            "y": corr.index.tolist(),
            "colorscale": "RdBu",
            "zmid": 0,
        }],
        "layout": {"title": "Feature Correlation Matrix", "height": 600}
    })

    # 4. Box plots by target
    for col in feature_cols[:4]:
        pos_vals = df[df[target] == 1][col].dropna().tolist()[:2000]
        neg_vals = df[df[target] == 0][col].dropna().tolist()[:2000]
        charts.append({
            "title": f"Box Plot: {col}",
            "type": "box",
            "data": [
                {"type": "box", "y": pos_vals, "name": "CVD+", "marker": {"color": "#e74c3c"}},
                {"type": "box", "y": neg_vals, "name": "CVD−", "marker": {"color": "#3498db"}}
            ],
            "layout": {"title": f"{col} by CVD Status"}
        })

    # 5. Feature importance (correlation with target)
    target_corr = df[feature_cols].corrwith(df[target]).abs().sort_values(ascending=True)
    charts.append({
        "title": "Feature-Target Correlation",
        "type": "bar",
        "data": [{
            "type": "bar",
            "x": target_corr.values.tolist(),
            "y": target_corr.index.tolist(),
            "orientation": "h",
            "marker": {"color": "#2ecc71",
                       "colorscale": "Viridis",
                       "color": target_corr.values.tolist()}
        }],
        "layout": {"title": "Feature Correlation with CVD Risk", "height": 500}
    })

    # 6. Age vs Risk (clinical insight)
    if "age" in df.columns or "age_decade" in df.columns:
        age_col = "age_decade" if "age_decade" in df.columns else "age"
        age_risk = df.groupby(age_col)[target].mean().reset_index()
        charts.append({
            "title": "Age vs CVD Risk",
            "type": "scatter",
            "data": [{
                "type": "scatter",
                "x": age_risk[age_col].tolist(),
                "y": (age_risk[target] * 100).round(1).tolist(),
                "mode": "lines+markers",
                "marker": {"size": 10, "color": "#e74c3c"},
                "line": {"width": 2}
            }],
            "layout": {"title": "Age Group vs CVD Risk %",
                       "xaxis": {"title": "Age"}, "yaxis": {"title": "CVD Risk %"}}
        })

    return charts


def _compute_summary_stats(df: pd.DataFrame, target: str) -> dict[str, Any]:
    num_df = df.select_dtypes(include=[np.number])
    desc = num_df.describe().round(3)
    return {
        "shape": list(df.shape),
        "target_col": target,
        "class_balance": df[target].value_counts(normalize=True).round(3).to_dict(),
        "describe": {str(k): {str(kk): float(vv) if hasattr(vv,"item") else vv for kk,vv in v.items()} for k,v in desc.to_dict().items()}
    }


def _generate_html(charts: list[dict], stats: dict, df: pd.DataFrame, target: str) -> str:
    chart_html_parts = []
    for i, chart in enumerate(charts):
        data_json = json.dumps(chart["data"])
        layout_json = json.dumps(chart.get("layout", {}))
        chart_html_parts.append(f"""
        <div class="chart-card">
          <h3>{chart['title']}</h3>
          <div id="chart_{i}" style="height:420px;"></div>
          <script>Plotly.newPlot('chart_{i}', {data_json}, {layout_json},
            {{responsive:true, displayModeBar:false}});</script>
        </div>""")

    balance = stats["class_balance"]
    balance_html = "".join(f"<li>Class {k}: <strong>{v*100:.1f}%</strong></li>"
                           for k, v in balance.items())

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EDA Report — CVD Risk Intelligence Platform</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #2c3e50; }}
  header {{ background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
             color: white; padding: 30px 40px; }}
  header h1 {{ font-size: 2rem; margin-bottom: 8px; }}
  .container {{ max-width: 1400px; margin: 0 auto; padding: 30px 20px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                  gap: 16px; margin: 24px 0; }}
  .stat-card {{ background: white; border-radius: 12px; padding: 20px; text-align: center;
                 box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  .stat-card .value {{ font-size: 2rem; font-weight: bold; color: #3498db; }}
  .stat-card .label {{ color: #7f8c8d; margin-top: 6px; font-size: 0.9rem; }}
  .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
                   gap: 24px; }}
  .chart-card {{ background: white; border-radius: 12px; padding: 24px;
                  box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  .chart-card h3 {{ font-size: 1rem; color: #7f8c8d; margin-bottom: 12px;
                    text-transform: uppercase; letter-spacing: 0.05em; }}
  .section-title {{ font-size: 1.4rem; font-weight: 600; margin: 32px 0 16px;
                     padding-left: 12px; border-left: 4px solid #3498db; }}
  .balance-card {{ background: white; border-radius: 12px; padding: 20px;
                    box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
  footer {{ text-align: center; padding: 24px; color: #95a5a6; font-size: 0.85rem; margin-top: 40px; }}
</style></head><body>
<header>
  <h1>🏥 CVD Risk Intelligence Platform</h1>
  <p>Exploratory Data Analysis Report &nbsp;|&nbsp; {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
</header>
<div class="container">

  <div class="stats-grid">
    <div class="stat-card"><div class="value">{stats['shape'][0]:,}</div><div class="label">Total Records</div></div>
    <div class="stat-card"><div class="value">{stats['shape'][1]}</div><div class="label">Features</div></div>
    <div class="stat-card"><div class="value">{target}</div><div class="label">Target Column</div></div>
    <div class="stat-card"><div class="value">{len([c for c in list(stats['describe'].keys())])}</div><div class="label">Numeric Features</div></div>
  </div>

  <div class="balance-card" style="margin-bottom:24px;">
    <h3 style="margin-bottom:10px;">🎯 Class Distribution</h3>
    <ul>{balance_html}</ul>
  </div>

  <div class="section-title">📊 Clinical Visualizations</div>
  <div class="charts-grid">
    {"".join(chart_html_parts)}
  </div>

</div>
<footer>CVD Risk Intelligence Platform | Australian Healthcare Compliant | ISO 27001 | APP Principles</footer>
</body></html>"""


def run() -> dict[str, Any]:
    log.info("Agent 4: EDA starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_PATH.exists():
        # Fallback: try cleaned dataset
        fallback = Path("outputs/02_data_cleaning/cleaned_dataset.parquet")
        if fallback.exists():
            df = pd.read_parquet(fallback)
        else:
            log.error("No input dataset found")
            return {"success": False, "artifact": ""}
    else:
        df = pd.read_parquet(INPUT_PATH)

    target = _infer_target(df)
    df[target] = df[target].astype(float)  # ensure JSON-serializable
    log.info("EDA on dataset", rows=len(df), cols=len(df.columns), target=target)

    charts = _generate_plotly_charts(df, target)
    stats = _compute_summary_stats(df, target)

    html_path = OUTPUT_DIR / "eda_report.html"
    html_path.write_text(_generate_html(charts, stats, df, target), encoding="utf-8")

    # Save stats JSON for downstream agents
    stats_path = OUTPUT_DIR / "eda_stats.json"
    with stats_path.open("w") as f:
        json.dump(stats, f, indent=2, default=str)

    log.info("Agent 4 complete", report=str(html_path), charts=len(charts))
    return {"success": True, "artifact": str(html_path)}


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
