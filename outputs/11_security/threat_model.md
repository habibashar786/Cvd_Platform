# CVD Platform — Threat Model (STRIDE)

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
