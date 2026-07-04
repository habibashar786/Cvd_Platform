# CVD Risk Intelligence Platform — SDD Specification Suite
# All 15 Agent Specifications | Spec-Driven Development

---

## AGENT 1 — Dataset Discovery Agent

### Requirement
Locate, profile, and catalog all spreadsheet/data files in `cvd risk dataset/`.

### Specification
- Scan for `.csv`, `.xlsx`, `.xls`, `.parquet`, `.json`
- Profile each file: shape, dtypes, null%, unique counts, descriptive stats
- Infer target column heuristically (binary column or name match)
- Compute SHA-256 checksum per file
- Generate `dataset_catalog.json` and `data_dictionary.md`

### Acceptance Criteria
- [ ] At least one dataset file discovered
- [ ] `dataset_catalog.json` is valid JSON with `files[]` array
- [ ] Each file entry contains: filename, rows, columns, column_profiles, target_column
- [ ] `data_dictionary.md` contains a markdown table per file
- [ ] SHA-256 checksum logged for each file

### Risk Assessment
- **LOW**: No PII risk at discovery phase (metadata only)
- **MEDIUM**: Incorrect target column inference could cascade to wrong model training

### Test Cases
- TC-01: CSV file discovered and profiled correctly
- TC-02: Excel file discovered and profiled correctly
- TC-03: Binary column correctly identified as target
- TC-04: Missing file → graceful error, not crash
- TC-05: Checksum changes if file is modified

---

## AGENT 2 — Data Cleaning Agent

### Requirement
Remove noise, fix missing values, deduplicate, handle outliers, score quality.

### Specification
- Load primary dataset (largest by row count from catalog)
- Fix column names: lowercase, strip, replace spaces
- Remove duplicates
- Impute missing: median for numeric, mode for categorical
- Drop columns with >60% missing
- Cap outliers at ±3σ (Z-score)
- Type coercion for binary and age columns
- Compute data quality score: completeness×0.5 + uniqueness×0.3 + retention×0.2

### Acceptance Criteria
- [ ] `cleaned_dataset.parquet` saved to outputs/02_data_cleaning/
- [ ] `data_quality_report.html` generated with all treatment sections
- [ ] Quality score ≥ 70 (minimum acceptable)
- [ ] No remaining null values in output (except legitimately sparse columns)
- [ ] HTML report shows: duplicates removed, missing treatments, outlier capping

### Risk Assessment
- **HIGH**: Over-aggressive outlier capping could remove clinically valid extremes (e.g., BP=180)
- **MEDIUM**: Wrong imputation strategy (mean vs median) could bias clinical distributions

### Test Cases
- TC-01: Duplicate rows removed and counted
- TC-02: Numeric nulls imputed with column median
- TC-03: Categorical nulls imputed with column mode
- TC-04: Column with 80% missing → dropped
- TC-05: Outlier value (age=999) → capped
- TC-06: Quality score returns value between 0 and 100

---

## AGENT 3 — Data Preprocessing Agent

### Requirement
Normalize features, encode categoricals, engineer CVD-domain features, resolve class imbalance.

### Specification
- Load `cleaned_dataset.parquet`
- Engineer features: pulse_pressure, bmi, age_decade (if source cols present)
- Encode categoricals: LabelEncoder (≤3 classes), OneHot (>3 classes)
- Scale: RobustScaler for clinical measurements, StandardScaler for others
- Evaluate class imbalance; apply best of: SMOTE, ADASYN, BorderlineSMOTE, SMOTETomek
- Save `processed_dataset.parquet` and `scalers.pkl`

### Acceptance Criteria
- [ ] `processed_dataset.parquet` exists and loads cleanly
- [ ] `scalers.pkl` exists (for inference pipeline)
- [ ] Class distribution post-resampling: minority class ≥ 35%
- [ ] No object/string columns remain (all encoded)
- [ ] `preprocessing_report.json` documents all transformations

### Risk Assessment
- **HIGH**: SMOTE can introduce synthetic patients that don't reflect real clinical distribution
- **MEDIUM**: Scaling before train/test split causes data leakage (MUST split first in production)

### Implementation Note
> ⚠️ For production: fit scalers ONLY on training set, transform test set separately.
> Current implementation is for research/EDA — refactor before clinical deployment.

### Test Cases
- TC-01: pulse_pressure = ap_hi - ap_lo (correctly computed)
- TC-02: BMI in range 10–60 for all patients
- TC-03: After SMOTE, minority class ≥ 35%
- TC-04: All categorical columns encoded to numeric
- TC-05: scalers.pkl is loadable with pickle

---

## AGENT 4 — EDA Agent

### Requirement
Generate publication-quality, interactive visualizations covering distribution, correlation, and clinical insights.

### Specification
Mandatory visualizations:
1. Target class distribution (pie/donut)
2. Feature distributions by CVD status (histogram overlay)
3. Correlation heatmap (top 15 features)
4. Box plots by CVD status (top 4 clinical features)
5. Feature-target correlation bar chart
6. Age vs CVD Risk % (clinical insight)

### Acceptance Criteria
- [ ] `eda_report.html` exists and opens in browser
- [ ] At least 6 distinct chart types present
- [ ] All charts are interactive (Plotly)
- [ ] Target class balance shown
- [ ] No patient-identifiable data in any chart label

### Risk Assessment
- **LOW**: Visual reports don't expose raw data
- **LOW**: Plotly CDN dependency (offline fallback: bundle plotly.js)

### Test Cases
- TC-01: HTML file size > 100KB (charts rendered)
- TC-02: "Target Class Distribution" present in HTML
- TC-03: "Correlation" present in HTML
- TC-04: No Medicare numbers in output

---

## AGENT 5 — Statistical Analysis Agent

### Requirement
Identify statistically significant CVD risk factors using formal hypothesis tests.

### Specification
- Chi-square test for all categorical features vs target
- T-test + Mann-Whitney U for all numeric features vs target (binary groups)
- Kruskal-Wallis for multi-class comparisons
- Report: test statistic, p-value, significance (p < 0.05)
- Identify top predictive factors and risk drivers

### Acceptance Criteria
- [ ] `statistical_report.html` generated
- [ ] `statistical_summary.json` with all test results
- [ ] p-values correctly computed (not hardcoded)
- [ ] Significant features (p<0.05) highlighted in report

### Test Cases
- TC-01: Chi-square correctly identifies known categorical association
- TC-02: Mann-Whitney detects mean difference between CVD groups
- TC-03: p-values in range [0, 1]

---

## AGENT 6 — Machine Learning Agent

### Requirement
Train, evaluate, and select the best CVD risk prediction model across 12+ algorithms.

### Specification
Train: LogReg, DecisionTree, RandomForest, NaiveBayes, KNN, SVM, GradientBoosting,
       AdaBoost, ExtraTrees, XGBoost, LightGBM, CatBoost
Evaluate: Accuracy, Balanced Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, MCC,
          Sensitivity, Specificity, Confusion Matrix (with clinical interpretation)
Select best by: **ROC-AUC** (primary) then F1 (tiebreaker)
Save: best_model.pkl, all individual model .pkl files, model_card.md

### Acceptance Criteria
- [ ] ≥8 models trained successfully
- [ ] `model_metrics.json` contains all metrics per model
- [ ] `best_model.pkl` is loadable with pickle
- [ ] `model_card.md` contains intended use, limitations, compliance
- [ ] ROC-AUC of best model ≥ 0.75 (clinical threshold)
- [ ] Confusion matrix includes clinical interpretation text

### Risk Assessment
- **CRITICAL**: False Negatives (missed CVD) more dangerous than False Positives
- **HIGH**: Model trained on one population may not generalize to all Australian demographics
- **MEDIUM**: CatBoost/XGBoost version mismatch across environments

### Test Cases
- TC-01: All 6 baseline models train without error
- TC-02: At least one ensemble model achieves ROC-AUC > 0.75
- TC-03: best_model.pkl contains model + feature_columns + target_column
- TC-04: Clinical interpretation in confusion matrix is non-empty
- TC-05: model_card.md mentions "Australian" compliance

---

## AGENT 7 — Explainable AI Agent

### Requirement
Generate SHAP and LIME explanations for global model behavior and individual patient predictions.

### Specification
SHAP:
  - Try TreeExplainer first; fallback to KernelExplainer
  - Global: mean |SHAP| per feature (top 20)
  - Local: top 10 factors per patient with clinical narrative
  - Sample max 500 records for performance

LIME:
  - LimeTabularExplainer on same sample
  - Per-patient: feature contributions + CVD probability
  - Generate for first 3 patients minimum

### Acceptance Criteria
- [ ] `shap_report.html` with interactive global importance chart
- [ ] At least 3 patient-level SHAP explanations with clinical narrative
- [ ] `lime_report.html` with CVD probability per patient
- [ ] `xai_summary.json` captures all results
- [ ] No model predictions stored with patient identifiers

### Test Cases
- TC-01: SHAP report renders without JS errors
- TC-02: Global importance ranking is sorted descending
- TC-03: Clinical narrative is non-empty for each patient
- TC-04: LIME probabilities sum to ~1.0 per patient

---

## AGENT 13 — Guardrail Agent

### Requirement
Final security gate before deployment. Zero critical issues required.

### Specification
Scan all output files for:
  - PII patterns: Medicare, TFN, email, phone, DOB, patient names
  - Prompt injection patterns (15+ patterns)
  - Hallucination triggers in clinical text
Check: essential_eight compliance, APP principles, threat model

### Acceptance Criteria
- [ ] `guardrail_report.json` status = "PASS" (0 critical issues)
- [ ] `threat_model.md` generated with STRIDE analysis
- [ ] All scanned files return status CLEAN or REVIEW_NEEDED
- [ ] If status = FAIL, pipeline MUST NOT proceed to deployment

### Risk Assessment
- **CRITICAL**: Any PII exposure violates Australian Privacy Act APP Principle 11
- **CRITICAL**: Prompt injection in clinical Q&A could generate dangerous advice

### Test Cases
- TC-01: Medicare number pattern → BLOCKED
- TC-02: "ignore all previous instructions" → CRITICAL finding
- TC-03: Clean clinical text → CLEAN status
- TC-04: Hallucination trigger "definitely no CVD" → MEDIUM finding

---

## AGENT 14 — Quality Control Agent

### Requirement
Cross-validate all pipeline outputs, enforce success criteria, issue release recommendation.

### Specification
Check artifacts: all 15 output folders have expected files
Check model: ROC-AUC ≥ 0.75
Check security: guardrail status = PASS
Check pipeline: audit trail has entries for all agents
Issue: APPROVED | CONDITIONAL | REJECTED with justification

### Acceptance Criteria
- [ ] `qc_report.html` generated with traffic-light status
- [ ] `qc_report.json` has criteria_passed field
- [ ] APPROVED only if all mandatory artifacts present AND ROC-AUC ≥ 0.75
- [ ] CONDITIONAL if minor gaps (optional agents skipped)
- [ ] REJECTED if critical artifacts missing or security failed

### Test Cases
- TC-01: All artifacts present → APPROVED
- TC-02: Missing best_model.pkl → CONDITIONAL or REJECTED
- TC-03: ROC-AUC = 0.60 → CONDITIONAL
- TC-04: Guardrail FAIL → status CONDITIONAL at minimum
