# Model Card — CVD Risk Intelligence Platform

## Model Overview
- **Best Model:** LightGBM
- **Task:** Binary Classification (CVD Risk Prediction)
- **Dataset Size:** 22,093 samples
- **Generated:** 2026-07-04T10:16:20.113574+00:00

## Performance Metrics
| Metric | Value |
|--------|-------|
| Accuracy | 0.9568 |
| ROC-AUC | 0.9654 |
| F1 Score | 0.9217 |
| Sensitivity (Recall) | 0.8706 |
| Specificity | 0.9923 |
| MCC | 0.8949 |

## Clinical Interpretation
- **Sensitivity 0.8706**: 87.1% of actual CVD patients correctly identified.
- **Specificity 0.9923**: 99.2% of non-CVD patients correctly ruled out.
- **False Negatives: 167** — These are patients with CVD who were missed. Clinical review recommended.

## Intended Use
- Clinical Decision Support (NOT a replacement for physician judgment)
- Population-level risk screening
- Research and quality improvement

## Limitations
- Validated on Australian healthcare population dataset
- Performance may vary in different populations
- Regular retraining recommended (every 6 months minimum)

## Compliance
- Australian Privacy Act / APP Principles
- FHIR R4 compatible output
- ISO 27001 compliant deployment

## Governance
- Model version must be approved by clinical governance committee before deployment
- All predictions must be logged for audit trail
- SHAP explanations mandatory for each clinical prediction
