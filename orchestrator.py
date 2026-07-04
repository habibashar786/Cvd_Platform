"""
CVD Risk Intelligence Platform — Master Orchestrator
Runs all 15 agents in sequence with QC gates and audit trail.

Usage:
    python orchestrator.py [--from-agent N] [--to-agent N] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger()

AGENTS = [
    {"id": 1,  "name": "Dataset Discovery Agent",    "module": "agents.01_discovery.agent"},
    {"id": 2,  "name": "Data Cleaning Agent",         "module": "agents.02_cleaning.agent"},
    {"id": 3,  "name": "Data Preprocessing Agent",    "module": "agents.03_preprocessing.agent"},
    {"id": 4,  "name": "EDA Agent",                   "module": "agents.04_eda.agent"},
    {"id": 5,  "name": "Statistical Analysis Agent",  "module": "agents.05_statistics.agent"},
    {"id": 6,  "name": "Machine Learning Agent",      "module": "agents.06_ml.agent"},
    {"id": 7,  "name": "Explainable AI Agent",        "module": "agents.07_xai.agent"},
    {"id": 8,  "name": "Graph Intelligence Agent",    "module": "agents.08_graph.agent"},
    {"id": 9,  "name": "Vector Database Agent",       "module": "agents.09_vector.agent"},
    {"id": 10, "name": "Generative AI / RAG Agent",   "module": "agents.10_rag.agent"},
    {"id": 11, "name": "Security Operations Agent",   "module": "agents.11_security.agent"},
    {"id": 12, "name": "Deployment Agent",            "module": "agents.12_deployment.agent"},
    {"id": 13, "name": "Guardrail Agent",             "module": "agents.13_guardrail.agent"},
    {"id": 14, "name": "Quality Control Agent",       "module": "agents.14_qc.agent"},
    {"id": 15, "name": "Code Review Agent",           "module": "agents.15_codereview.agent"},
]

AUDIT_LOG = Path("outputs/15_audit/audit_trail.jsonl")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _write_audit(event: dict[str, Any]) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


def _emit_message(sender: str, receiver: str, msg_type: str, artifact: str) -> dict:
    msg = {
        "sender": sender,
        "receiver": receiver,
        "message_type": msg_type,
        "artifact": artifact,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checksum": _sha256(artifact),
    }
    _write_audit({"type": "agent_message", **msg})
    return msg


def run_agent(agent_meta: dict, dry_run: bool = False) -> bool:
    agent_id = agent_meta["id"]
    name = agent_meta["name"]
    module_path = agent_meta["module"]

    log.info("Starting agent", agent_id=agent_id, name=name)
    _write_audit({
        "type": "agent_start",
        "agent_id": agent_id,
        "agent_name": name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    if dry_run:
        log.info("DRY RUN — skipping execution", agent=name)
        return True

    try:
        import importlib
        mod = importlib.import_module(module_path)
        result = mod.run()
        success = result.get("success", False) if isinstance(result, dict) else bool(result)
        artifact = result.get("artifact", "") if isinstance(result, dict) else ""

        _write_audit({
            "type": "agent_complete",
            "agent_id": agent_id,
            "agent_name": name,
            "success": success,
            "artifact": artifact,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        if agent_id < 15:
            next_agent = AGENTS[agent_id]["name"]
            _emit_message(name, next_agent, "handoff", artifact)

        log.info("Agent complete", agent=name, success=success, artifact=artifact)
        return success

    except Exception as exc:
        log.error("Agent failed", agent=name, error=str(exc))
        _write_audit({
            "type": "agent_error",
            "agent_id": agent_id,
            "agent_name": name,
            "error": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="CVD Platform Orchestrator")
    parser.add_argument("--from-agent", type=int, default=1, metavar="N")
    parser.add_argument("--to-agent", type=int, default=15, metavar="N")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log.info("CVD Platform starting", from_agent=args.from_agent, to_agent=args.to_agent)

    _write_audit({
        "type": "pipeline_start",
        "from_agent": args.from_agent,
        "to_agent": args.to_agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    agents_to_run = [a for a in AGENTS if args.from_agent <= a["id"] <= args.to_agent]
    failed = []

    for agent in agents_to_run:
        ok = run_agent(agent, dry_run=args.dry_run)
        if not ok:
            failed.append(agent["name"])
            log.error("Pipeline halted at agent", agent=agent["name"])
            # QC Gate: halt on failure unless it's a non-critical agent
            if agent["id"] not in {8, 9, 10}:  # Graph/Vector/RAG are optional
                break

    status = "PASSED" if not failed else "FAILED"
    _write_audit({
        "type": "pipeline_complete",
        "status": status,
        "failed_agents": failed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    log.info("Pipeline complete", status=status, failed=failed)
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
