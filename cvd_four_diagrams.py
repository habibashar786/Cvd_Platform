from __future__ import annotations
import argparse
import re
from pathlib import Path
from typing import Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END


# ===================================================================
# 1.  SECURITY ARCHITECTURE
#     Five-layer defence: Identity -> Red/Blue/Green -> Vibe Diff -> Quarantine
# ===================================================================

class SecurityState(TypedDict):
    request:           Optional[str]
    identity_result:   Optional[dict]
    red_team_report:   Optional[dict]
    blue_team_report:  Optional[dict]
    green_team_report: Optional[dict]
    mfa_diff_result:   Optional[dict]
    quarantine_status: Optional[str]
    security_cleared:  Optional[bool]

def s_identity(state):    return state
def s_red_team(state):    return state
def s_blue_team(state):   return state
def s_green_team(state):  return state
def s_vibe_diff(state):   return state
def s_quarantine(state):  return state

def build_security_graph():
    b = StateGraph(SecurityState)
    b.add_node("identity",    s_identity)
    b.add_node("red_team",    s_red_team)
    b.add_node("blue_team",   s_blue_team)
    b.add_node("green_team",  s_green_team)
    b.add_node("vibe_diff",   s_vibe_diff)
    b.add_node("quarantine",  s_quarantine)

    b.set_entry_point("identity")
    # Identity fans out to all three security teams in parallel
    b.add_edge("identity",   "red_team")
    b.add_edge("identity",   "blue_team")
    b.add_edge("identity",   "green_team")
    # All three converge at vibe_diff gate
    b.add_edge("red_team",   "vibe_diff")
    b.add_edge("blue_team",  "vibe_diff")
    b.add_edge("green_team", "vibe_diff")
    # Vibe diff clears or escalates to quarantine
    b.add_edge("vibe_diff",  "quarantine")
    b.add_edge("quarantine", END)
    return b.compile()


# ===================================================================
# 2.  GCP DEPLOYMENT ARCHITECTURE
#     Cloud Armor -> LB -> GKE (3 pods) -> GCP Managed Services
# ===================================================================

class GCPDeployState(TypedDict):
    request:              Optional[str]
    armor_verdict:        Optional[str]
    lb_routed:            Optional[bool]
    fastapi_response:     Optional[dict]
    streamlit_served:     Optional[bool]
    orchestrator_ran:     Optional[bool]
    storage_written:      Optional[bool]
    vector_updated:       Optional[bool]
    audit_ledger_updated: Optional[bool]

def gcp_armor(state):         return state
def gcp_lb(state):            return state
def gcp_fastapi(state):       return state
def gcp_streamlit(state):     return state
def gcp_orchestrator(state):  return state
def gcp_storage(state):       return state
def gcp_vector(state):        return state
def gcp_spanner(state):       return state
def gcp_monitoring(state):    return state

def build_gcp_graph():
    b = StateGraph(GCPDeployState)
    b.add_node("cloud_armor",     gcp_armor)
    b.add_node("load_balancer",   gcp_lb)
    b.add_node("fastapi_pod",     gcp_fastapi)
    b.add_node("streamlit_pod",   gcp_streamlit)
    b.add_node("orchestrator_pod",gcp_orchestrator)
    b.add_node("cloud_storage",   gcp_storage)
    b.add_node("vertex_vector_db",gcp_vector)
    b.add_node("cloud_spanner",   gcp_spanner)
    b.add_node("cloud_monitoring",gcp_monitoring)

    b.set_entry_point("cloud_armor")
    b.add_edge("cloud_armor",      "load_balancer")
    # LB fans out to the three GKE pods
    b.add_edge("load_balancer",    "fastapi_pod")
    b.add_edge("load_balancer",    "streamlit_pod")
    b.add_edge("load_balancer",    "orchestrator_pod")
    # Pods write to GCP managed services
    b.add_edge("fastapi_pod",      "cloud_storage")
    b.add_edge("orchestrator_pod", "cloud_storage")
    b.add_edge("orchestrator_pod", "vertex_vector_db")
    b.add_edge("orchestrator_pod", "cloud_spanner")
    # All services report to monitoring
    for n in ["cloud_storage","vertex_vector_db","cloud_spanner","fastapi_pod","streamlit_pod"]:
        b.add_edge(n, "cloud_monitoring")
    b.add_edge("cloud_monitoring", END)
    return b.compile()


# ===================================================================
# 3.  GUARDRAIL ARCHITECTURE
#     Sequential 4-check gate: threat -> PII -> bias -> compliance -> decision
# ===================================================================

class GuardrailState(TypedDict):
    pipeline_bundle:      Optional[dict]
    threat_scan_result:   Optional[dict]
    pii_scan_result:      Optional[dict]
    bias_audit_result:    Optional[dict]
    compliance_result:    Optional[dict]
    critical_issues:      Optional[int]
    guardrail_verdict:    Optional[str]   # APPROVED | BLOCKED
    threat_model_path:    Optional[str]
    guardrail_report:     Optional[str]

def g_threat_scan(state):   return state
def g_pii_detect(state):    return state
def g_bias_audit(state):    return state
def g_compliance(state):    return state
def g_decision(state):      return state
def g_blocked(state):       return state
def g_approved(state):      return state

def guardrail_router(state: GuardrailState) -> str:
    """Route based on critical_issues count."""
    return "blocked" if (state.get("critical_issues") or 0) > 0 else "approved"

def build_guardrail_graph():
    b = StateGraph(GuardrailState)
    b.add_node("threat_scan",  g_threat_scan)
    b.add_node("pii_detect",   g_pii_detect)
    b.add_node("bias_audit",   g_bias_audit)
    b.add_node("compliance",   g_compliance)
    b.add_node("decision",     g_decision)
    b.add_node("blocked",      g_blocked)
    b.add_node("approved",     g_approved)

    b.set_entry_point("threat_scan")
    # Strictly sequential - each check must pass before next
    b.add_edge("threat_scan", "pii_detect")
    b.add_edge("pii_detect",  "bias_audit")
    b.add_edge("bias_audit",  "compliance")
    b.add_edge("compliance",  "decision")
    # Conditional routing at decision gate
    b.add_conditional_edges(
        "decision",
        guardrail_router,
        {"blocked": "blocked", "approved": "approved"}
    )
    b.add_edge("blocked",  END)
    b.add_edge("approved", END)
    return b.compile()


# ===================================================================
# 4.  QUALITY CONTROL ARCHITECTURE
#     4 parallel checks -> verdict -> APPROVED / CONDITIONAL / REJECTED
# ===================================================================

class QCState(TypedDict):
    guardrail_report:      Optional[str]
    model_qc_result:       Optional[dict]
    data_qc_result:        Optional[dict]
    xai_qc_result:         Optional[dict]
    pipeline_qc_result:    Optional[dict]
    qc_score:              Optional[float]
    qc_status:             Optional[str]  # APPROVED | CONDITIONAL | REJECTED
    qc_report_path:        Optional[str]

def qc_model(state):     return state
def qc_data(state):      return state
def qc_xai(state):       return state
def qc_pipeline(state):  return state
def qc_verdict(state):   return state
def qc_approved(state):  return state
def qc_conditional(state): return state
def qc_rejected(state):  return state

def qc_router(state: QCState) -> str:
    score = state.get("qc_score") or 0.0
    if score >= 0.90:   return "approved"
    if score >= 0.70:   return "conditional"
    return "rejected"

def build_qc_graph():
    b = StateGraph(QCState)
    b.add_node("model_qc",     qc_model)
    b.add_node("data_qc",      qc_data)
    b.add_node("xai_qc",       qc_xai)
    b.add_node("pipeline_qc",  qc_pipeline)
    b.add_node("verdict",      qc_verdict)
    b.add_node("approved",     qc_approved)
    b.add_node("conditional",  qc_conditional)
    b.add_node("rejected",     qc_rejected)

    b.set_entry_point("model_qc")
    # 4 checks run in parallel from the same entry - wire them sequentially
    # for graph clarity (LangGraph executes linearly unless async)
    b.add_edge("model_qc",    "data_qc")
    b.add_edge("data_qc",     "xai_qc")
    b.add_edge("xai_qc",      "pipeline_qc")
    b.add_edge("pipeline_qc", "verdict")
    b.add_conditional_edges(
        "verdict",
        qc_router,
        {
            "approved":    "approved",
            "conditional": "conditional",
            "rejected":    "rejected",
        }
    )
    b.add_edge("approved",    END)
    b.add_edge("conditional", END)
    b.add_edge("rejected",    END)
    return b.compile()


# ===================================================================
# UTILITIES
# ===================================================================

DIAGRAMS = [
    ("security",   "Security defence architecture",      build_security_graph),
    ("gcp_deploy", "GCP cloud deployment architecture",  build_gcp_graph),
    ("guardrail",  "Guardrail agent flow",               build_guardrail_graph),
    ("qc",         "Quality control agentic gate",       build_qc_graph),
]

README_SECTIONS = {
    "security":   ("<!-- SECURITY_DIAGRAM_START -->",  "<!-- SECURITY_DIAGRAM_END -->"),
    "gcp_deploy": ("<!-- GCP_DIAGRAM_START -->",       "<!-- GCP_DIAGRAM_END -->"),
    "guardrail":  ("<!-- GUARDRAIL_DIAGRAM_START -->", "<!-- GUARDRAIL_DIAGRAM_END -->"),
    "qc":         ("<!-- QC_DIAGRAM_START -->",        "<!-- QC_DIAGRAM_END -->"),
}

def save_mmd(name: str, mermaid: str):
    path = Path(f"cvd_{name}_diagram.mmd")
    path.write_text(mermaid, encoding="utf-8")
    print(f"  [OK] Mermaid saved -> {path}")

def save_png(name: str, graph):
    try:
        png = graph.get_graph().draw_mermaid_png()
        path = Path(f"cvd_{name}_diagram.png")
        path.write_bytes(png)
        print(f"  [OK] PNG saved -> {path}")
    except Exception as e:
        print(f"  [!] PNG failed for {name}: {e}")
        print("      pip install playwright && playwright install chromium")

def update_readme(name: str, mermaid: str, readme_path: str = "README.md"):
    start, end = README_SECTIONS[name]
    readme = Path(readme_path)
    if not readme.exists():
        print(f"  [!] {readme_path} not found - skipping")
        return
    content = readme.read_text(encoding="utf-8")
    block = (
        f"{start}\n"
        f"<!-- Auto-generated by cvd_four_diagrams.py - do not edit -->\n"
        f"```mermaid\n{mermaid}```\n"
        f"{end}"
    )
    if start in content and end in content:
        pattern = re.escape(start) + r".*?" + re.escape(end)
        content = re.sub(pattern, block, content, flags=re.DOTALL)
    else:
        content = content.rstrip() + f"\n\n{block}\n"
    readme.write_text(content, encoding="utf-8")
    print(f"  [OK] README.md updated: {name} section")


# ===================================================================
# MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description="CVD - Four Specialised Architecture Diagrams")
    parser.add_argument("--save",          action="store_true", help="Save .mmd files")
    parser.add_argument("--png",           action="store_true", help="Save PNG files (needs playwright)")
    parser.add_argument("--update-readme", action="store_true", help="Inject diagrams into README.md")
    parser.add_argument("--readme-path",   default="README.md")
    args = parser.parse_args()

    for name, title, builder_fn in DIAGRAMS:
        print(f"\n{'='*60}")
        print(f"  {title.upper()}")
        print(f"{'='*60}")
        graph = builder_fn()
        mermaid = graph.get_graph().draw_mermaid()
        print(mermaid)
        if args.save:
            save_mmd(name, mermaid)
        if args.png:
            save_png(name, graph)
        if args.update_readme:
            update_readme(name, mermaid, args.readme_path)

    print("\n[Done] All four diagrams generated.")
    print("Paste any section into https://mermaid.live to preview.\n")

if __name__ == "__main__":
    main()
