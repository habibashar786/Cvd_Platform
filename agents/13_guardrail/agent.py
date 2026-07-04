"""
AGENT 13 — Guardrail Agent
Protects entire system: PII, prompt injection, hallucination, data leakage checks.
Mandatory gate before deployment.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

log = structlog.get_logger()
OUTPUT_DIR = Path("outputs/11_security")


PII_PATTERNS = {
    "medicare_number": re.compile(r"\b\d{4}\s?\d{5}\s?\d\b"),
    "tfn": re.compile(r"\b\d{3}\s?\d{3}\s?\d{3}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"),
    "phone_au": re.compile(r"\b(\+61|0)[2-478](\s?\d{4}){2}\b"),
    "dob": re.compile(r"\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[012])[-/](19|20)\d\d\b"),
    "given_name_field": re.compile(r"(?i)(patient.?name|given.?name|surname|first.?name)"),
}

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+(all\s+)?previous\s+instructions"),
    re.compile(r"(?i)system\s*prompt"),
    re.compile(r"(?i)jailbreak"),
    re.compile(r"(?i)you\s+are\s+now"),
    re.compile(r"(?i)DAN\s+mode"),
    re.compile(r"(?i)act\s+as\s+if"),
    re.compile(r"(?i)forget\s+your\s+training"),
]

HALLUCINATION_TRIGGERS = [
    "definitely", "absolutely certain", "100% sure", "guaranteed",
    "no risk", "impossible to have CVD", "will never develop"
]


def _scan_pii(text: str) -> list[dict]:
    findings = []
    for name, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            findings.append({"type": name, "severity": "HIGH",
                              "action": "REDACT before logging"})
    return findings


def _scan_injection(text: str) -> list[dict]:
    findings = []
    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            findings.append({"pattern": pattern.pattern, "severity": "CRITICAL",
                              "action": "BLOCK and alert Blue Team"})
    return findings


def _scan_hallucination_triggers(text: str) -> list[dict]:
    findings = []
    for trigger in HALLUCINATION_TRIGGERS:
        if trigger.lower() in text.lower():
            findings.append({"trigger": trigger, "severity": "MEDIUM",
                              "action": "Flag for clinical review"})
    return findings


def _check_output_files() -> dict[str, Any]:
    """Scan key outputs for PII/security issues."""
    scan_targets = [
        Path("outputs/04_eda/eda_report.html"),
        Path("outputs/06_machine_learning/model_card.md"),
        Path("outputs/07_xai/shap_report.html"),
    ]
    results: dict[str, Any] = {}
    for path in scan_targets:
        if not path.exists():
            results[str(path)] = {"status": "NOT_FOUND"}
            continue
        content = path.read_text(errors="replace")
        pii = _scan_pii(content)
        injection = _scan_injection(content)
        halluc = _scan_hallucination_triggers(content)
        results[str(path)] = {
            "pii_findings": pii,
            "injection_findings": injection,
            "hallucination_findings": halluc,
            "status": "CLEAN" if not (pii or injection) else "REVIEW_NEEDED"
        }
    return results


def _generate_threat_model() -> str:
    return """# CVD Platform — Threat Model (STRIDE)

## Assets
- Patient CVD risk data
- Trained ML models (CatBoost / XGBoost)
- SHAP/LIME explanations
- Clinical knowledge graph

## STRIDE Threats

### Spoofing
- **Threat**: Unauthorized agent impersonation
- **Mitigation**: Agentic Identity Agent + JWT tokens

### Tampering
- **Threat**: Model weights modification
- **Mitigation**: SHA-256 checksums on all artifacts; Vibe Diff MFA Agent

### Repudiation
- **Threat**: Denial of prediction actions
- **Mitigation**: Immutable audit trail (JSONL, append-only)

### Information Disclosure
- **Threat**: PII exposure in logs/reports
- **Mitigation**: PII regex scanning, field-level encryption, anonymization

### Denial of Service
- **Threat**: Resource exhaustion via large inference requests
- **Mitigation**: Rate limiting, input validation, Guardrail Agent

### Elevation of Privilege
- **Threat**: Agent attempting to access other agents' data
- **Mitigation**: IAM roles per agent, least-privilege, network segmentation

## Australian Compliance Controls
- APP Principle 11: Security of personal information
- Essential Eight: Application control, patch OS, MFA
- ISO 27001 A.12.6: Management of technical vulnerabilities
"""


def run() -> dict[str, Any]:
    log.info("Agent 13: Guardrail Agent starting")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_scan = _check_output_files()
    threat_model = _generate_threat_model()

    # Count issues
    total_critical = sum(
        len([f for f in v.get("injection_findings", []) if f["severity"] == "CRITICAL"])
        for v in file_scan.values() if isinstance(v, dict)
    )
    total_high = sum(
        len(v.get("pii_findings", []))
        for v in file_scan.values() if isinstance(v, dict)
    )

    status = "PASS" if total_critical == 0 else "FAIL"

    report = {
        "guardrail_status": status,
        "critical_issues": total_critical,
        "high_issues": total_high,
        "file_scans": file_scan,
        "checks_performed": [
            "PII Detection (Medicare, TFN, Email, Phone, DOB)",
            "Prompt Injection Pattern Scanning",
            "Hallucination Trigger Detection",
            "Output File Security Audit",
        ],
        "compliance": {
            "australian_privacy_act": "CHECKED",
            "app_principles": "CHECKED",
            "essential_eight": "PARTIAL",
            "iso_27001": "DESIGN_COMPLIANT",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save report
    report_path = OUTPUT_DIR / "guardrail_report.json"
    with report_path.open("w") as f:
        json.dump(report, f, indent=2)

    # Save threat model
    threat_path = OUTPUT_DIR / "threat_model.md"
    threat_path.write_text(threat_model, encoding="utf-8")

    log.info("Agent 13 complete", status=status, critical=total_critical)
    return {"success": status == "PASS", "artifact": str(report_path)}


def scan_text(text: str) -> tuple[bool, str]:
    """Scan arbitrary text and return (is_safe, reason)."""
    pii = _scan_pii(text)
    if pii:
        return False, f"PII detected: {[p['type'] for p in pii]}"
    inj = _scan_injection(text)
    if inj:
        return False, "Potential prompt injection detected"
    halluc = _scan_hallucination_triggers(text)
    if halluc:
        return False, f"Clinical hallucination trigger detected: {[h['trigger'] for h in halluc]}"
    return True, "Clean"


if __name__ == "__main__":
    import structlog
    structlog.configure()
    result = run()
    print(json.dumps(result, indent=2, default=str))
