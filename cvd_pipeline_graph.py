from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from typing import Optional
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END


# ─── 1. Shared Pipeline State ────────────────────────────────────────────────
# Every artifact that flows between agents is declared here as an Optional field.
# Adding a new agent = add its output field here AND wire it in build_graph().

class CVDPipelineState(TypedDict):
    # Agent 1  — Discovery
    dataset_catalog:      Optional[dict]
    data_dictionary:      Optional[str]
    # Agent 2  — Cleaning
    cleaned_path:         Optional[str]
    quality_report:       Optional[str]
    # Agent 3  — Preprocessing
    processed_path:       Optional[str]
    scalers_path:         Optional[str]
    # Agent 4  — EDA
    eda_report:           Optional[str]
    # Agent 5  — Statistical Analysis
    stats_report:         Optional[str]
    # Agent 6  — Machine Learning
    best_model_path:      Optional[str]
    model_metrics:        Optional[dict]
    model_card:           Optional[str]
    # Agent 7  — Explainable AI
    shap_report:          Optional[str]
    lime_report:          Optional[str]
    # Agent 8  — Graph Intelligence
    knowledge_graph:      Optional[str]
    # Agent 9  — Vector Database
    vector_index:         Optional[str]
    # Agent 10 — RAG / GenAI
    rag_system:           Optional[str]
    # Agent 11 — Security Ops
    security_audit:       Optional[str]
    # Agent 12 — Deployment
    deployment_artifacts: Optional[str]
    # Agent 13 — Guardrail
    guardrail_report:     Optional[str]
    threat_model:         Optional[str]
    # Agent 14 — Quality Control
    qc_report:            Optional[str]
    # Agent 15 — Code Review
    final_release:        Optional[str]


# ─── 2. Agent Stub Functions ──────────────────────────────────────────────────
# These are pass-through stubs. The real logic lives in agents/XX_*/agent.py.
# LangGraph only needs the function signatures to build the graph topology.

def agent_01_discovery(state: CVDPipelineState)    -> CVDPipelineState: return state
def agent_02_cleaning(state: CVDPipelineState)     -> CVDPipelineState: return state
def agent_03_preprocessing(state: CVDPipelineState)-> CVDPipelineState: return state
def agent_04_eda(state: CVDPipelineState)          -> CVDPipelineState: return state
def agent_05_stats(state: CVDPipelineState)        -> CVDPipelineState: return state
def agent_06_ml(state: CVDPipelineState)           -> CVDPipelineState: return state
def agent_07_xai(state: CVDPipelineState)          -> CVDPipelineState: return state
def agent_08_graph(state: CVDPipelineState)        -> CVDPipelineState: return state
def agent_09_vector(state: CVDPipelineState)       -> CVDPipelineState: return state
def agent_10_rag(state: CVDPipelineState)          -> CVDPipelineState: return state
def agent_11_security(state: CVDPipelineState)     -> CVDPipelineState: return state
def agent_12_deploy(state: CVDPipelineState)       -> CVDPipelineState: return state
def agent_13_guardrail(state: CVDPipelineState)    -> CVDPipelineState: return state
def agent_14_qc(state: CVDPipelineState)           -> CVDPipelineState: return state
def agent_15_review(state: CVDPipelineState)       -> CVDPipelineState: return state


# ─── 3. Graph Builder ─────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Wires the 15 agents into a LangGraph StateGraph.

    Topology mirrors the README architecture:

        discovery → cleaning → preprocessing ─┬─ eda   ─┐
                                               ├─ stats  ─┤
                                               └─ ml ────┼─→ xai ─────────────┐
                                                         └─→ graph_intel       │
                                                              → vector_db       │
                                                                → rag ─────────┤
                                                                               ↓
                                               security ← [eda, stats, xai, rag]
                                               → deployment → guardrail → qc → code_review → END
    """
    b = StateGraph(CVDPipelineState)

    # Register nodes — name : stub function
    b.add_node("01_discovery",    agent_01_discovery)
    b.add_node("02_cleaning",     agent_02_cleaning)
    b.add_node("03_preprocessing",agent_03_preprocessing)
    b.add_node("04_eda",          agent_04_eda)
    b.add_node("05_stats",        agent_05_stats)
    b.add_node("06_ml",           agent_06_ml)
    b.add_node("07_xai",          agent_07_xai)
    b.add_node("08_graph_intel",  agent_08_graph)
    b.add_node("09_vector_db",    agent_09_vector)
    b.add_node("10_rag",          agent_10_rag)
    b.add_node("11_security",     agent_11_security)
    b.add_node("12_deployment",   agent_12_deploy)
    b.add_node("13_guardrail",    agent_13_guardrail)
    b.add_node("14_qc",           agent_14_qc)
    b.add_node("15_code_review",  agent_15_review)

    # Entry point
    b.set_entry_point("01_discovery")

    # Linear spine: discovery → cleaning → preprocessing
    b.add_edge("01_discovery",     "02_cleaning")
    b.add_edge("02_cleaning",      "03_preprocessing")

    # Fan-out from preprocessing (3 parallel branches)
    b.add_edge("03_preprocessing", "04_eda")
    b.add_edge("03_preprocessing", "05_stats")
    b.add_edge("03_preprocessing", "06_ml")

    # ML sub-branches (xai + graph track)
    b.add_edge("06_ml",            "07_xai")
    b.add_edge("06_ml",            "08_graph_intel")

    # Graph track continuation
    b.add_edge("08_graph_intel",   "09_vector_db")
    b.add_edge("09_vector_db",     "10_rag")

    # Fan-in to Security Ops gate (all analysis outputs)
    for n in ["04_eda", "05_stats", "07_xai", "10_rag"]:
        b.add_edge(n, "11_security")

    # Linear tail: security → deployment → guardrail → qc → review → END
    b.add_edge("11_security",      "12_deployment")
    b.add_edge("12_deployment",    "13_guardrail")
    b.add_edge("13_guardrail",     "14_qc")
    b.add_edge("14_qc",            "15_code_review")
    b.add_edge("15_code_review",   END)

    return b.compile()


# ─── 4. Diagram Outputs ───────────────────────────────────────────────────────

def get_mermaid(graph) -> str:
    """Return raw Mermaid source from the compiled graph."""
    return graph.get_graph().draw_mermaid()


def save_png(graph, path: str = "cvd_architecture_diagram.png") -> None:
    """
    Save a rendered PNG using LangGraph's built-in PNG renderer.
    Requires:  pip install playwright && playwright install chromium
    Falls back gracefully if playwright is not installed.
    """
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        Path(path).write_bytes(png_bytes)
        print(f"[OK] PNG saved → {path}")
    except Exception as e:
        print(f"[!] PNG render failed ({e})")
        print("    Install playwright:  pip install playwright && playwright install chromium")
        print("    Or paste the Mermaid source into https://mermaid.live")


README_START_MARKER = "<!-- ARCHITECTURE_DIAGRAM_START -->"
README_END_MARKER   = "<!-- ARCHITECTURE_DIAGRAM_END -->"

def update_readme(graph, readme_path: str = "README.md") -> None:
    """
    Inject the live Mermaid diagram into README.md between marker comments.
    Adds the markers on first run if they don't exist yet.

    Add these two lines to your README.md where you want the diagram to appear:
        <!-- ARCHITECTURE_DIAGRAM_START -->
        <!-- ARCHITECTURE_DIAGRAM_END -->
    """
    readme = Path(readme_path)
    if not readme.exists():
        print(f"[!] {readme_path} not found. Skipping README update.")
        return

    content = readme.read_text(encoding="utf-8")
    mermaid = get_mermaid(graph)
    block = (
        f"{README_START_MARKER}\n"
        f"<!-- Auto-generated by cvd_pipeline_graph.py — do not edit manually -->\n"
        f"```mermaid\n{mermaid}```\n"
        f"{README_END_MARKER}"
    )

    if README_START_MARKER in content and README_END_MARKER in content:
        # Replace existing block
        pattern = re.escape(README_START_MARKER) + r".*?" + re.escape(README_END_MARKER)
        new_content = re.sub(pattern, block, content, flags=re.DOTALL)
    else:
        # Append at end of file on first run
        new_content = content.rstrip() + f"\n\n{block}\n"

    readme.write_text(new_content, encoding="utf-8")
    print(f"[OK] README.md updated with live architecture diagram")


# ─── 5. CLI Entry Point ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="CVD Pipeline — LangGraph Architecture Diagram Generator"
    )
    parser.add_argument("--save-png",      action="store_true",
                        help="Render and save diagram as PNG")
    parser.add_argument("--update-readme", action="store_true",
                        help="Inject live diagram into README.md")
    parser.add_argument("--png-path",      default="cvd_architecture_diagram.png",
                        help="Output path for PNG (default: cvd_architecture_diagram.png)")
    parser.add_argument("--readme-path",   default="README.md",
                        help="Path to README.md (default: README.md)")
    parser.add_argument("--all",           action="store_true",
                        help="Do everything: print + save PNG + update README")
    args = parser.parse_args()

    graph = build_graph()

    # Default: always print Mermaid source
    mermaid = get_mermaid(graph)
    print("\n== Live Mermaid Source =============================================")
    print(mermaid)
    print("====================================================================")
    print("Paste the above into https://mermaid.live to preview instantly\n")

    if args.save_png or args.all:
        save_png(graph, args.png_path)

    if args.update_readme or args.all:
        update_readme(graph, args.readme_path)


if __name__ == "__main__":
    main()
