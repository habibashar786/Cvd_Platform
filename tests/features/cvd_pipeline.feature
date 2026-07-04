# CVD Risk Intelligence Platform — BDD Feature Suite (Gherkin4)

Feature: CVD Risk Pipeline End-to-End

  Background:
    Given the CVD dataset folder exists at "cvd risk dataset"
    And the Python environment has all dependencies installed
    And the project structure is initialized

  # ============================
  # AGENT 1: Dataset Discovery
  # ============================
  Scenario: Discover and catalog all CVD datasets
    Given the dataset folder contains spreadsheet files
    When Agent 1 (Dataset Discovery) runs
    Then dataset_catalog.json is created in outputs/01_data_catalog
    And data_dictionary.md is created in outputs/01_data_catalog
    And all column types are profiled
    And the target column is identified

  # ============================
  # AGENT 2: Data Cleaning
  # ============================
  Scenario: Clean the CVD dataset
    Given dataset_catalog.json exists
    When Agent 2 (Data Cleaning) runs
    Then cleaned_dataset.parquet is created in outputs/02_data_cleaning
    And data_quality_report.html is created
    And the quality score is at least 70
    And no PII fields are exposed in any output

  Scenario: Handle missing values gracefully
    Given the dataset has columns with more than 5% missing values
    When Agent 2 applies imputation
    Then numeric columns are imputed with the median
    And categorical columns are imputed with the mode
    And columns with more than 60% missing are dropped

  # ============================
  # AGENT 3: Preprocessing
  # ============================
  Scenario: Preprocess and handle class imbalance
    Given cleaned_dataset.parquet exists
    When Agent 3 (Preprocessing) runs
    Then processed_dataset.parquet is created in outputs/03_preprocessing
    And scalers.pkl is saved for inference
    And class imbalance is resolved using the best resampling strategy

  Scenario: Select best resampling strategy
    Given the minority class is less than 40% of the dataset
    When Agent 3 evaluates SMOTE, BorderlineSMOTE, ADASYN, and SMOTETomek
    Then the strategy with the best balance ratio is selected
    And the selected strategy is logged in preprocessing_report.json

  # ============================
  # AGENT 4: EDA
  # ============================
  Scenario: Generate comprehensive EDA visualizations
    Given processed_dataset.parquet exists
    When Agent 4 (EDA) runs
    Then eda_report.html is created with at least 6 chart types
    And the target class distribution chart is present
    And the feature correlation heatmap is present
    And clinical insights charts are present

  # ============================
  # AGENT 6: Machine Learning
  # ============================
  Scenario: Benchmark all ML models
    Given processed_dataset.parquet exists
    When Agent 6 (ML) trains all models
    Then at least 8 models are trained and evaluated
    And model_metrics.json contains ROC-AUC, F1, Sensitivity, Specificity
    And the best model is saved to best_model.pkl
    And model_card.md is generated

  Scenario: Predict patient CVD risk
    Given the best model is loaded
    And a validated patient record is available
    When the clinician submits patient measurements
    Then the system predicts CVD risk (0 or 1)
    And provides a confidence score (probability)
    And logs the prediction to the audit trail

  # ============================
  # AGENT 7: Explainable AI
  # ============================
  Scenario: Generate SHAP global explanations
    Given best_model.pkl exists
    And processed_dataset.parquet exists
    When Agent 7 (XAI) runs SHAP analysis
    Then shap_report.html is created
    And global feature importance ranking is present
    And at least 3 patient-level local explanations are present

  Scenario: Generate LIME local explanations
    Given best_model.pkl exists
    When Agent 7 runs LIME analysis
    Then lime_report.html is created
    And each patient explanation includes feature contributions
    And CVD probability is shown per patient

  # ============================
  # AGENT 13: Guardrail
  # ============================
  Scenario: Detect PII in output files
    Given all output files have been generated
    When Agent 13 (Guardrail) scans output files
    Then no Medicare numbers are present in outputs
    And no Tax File Numbers are present in outputs
    And no patient names are present in outputs
    And the guardrail_report.json status is CLEAN

  Scenario: Block prompt injection attempts
    Given a malicious input containing "ignore all previous instructions"
    When Agent 13 evaluates the input
    Then the request is BLOCKED
    And the Blue Team Agent is alerted
    And the event is logged in the audit trail

  # ============================
  # AGENT 14: Quality Control
  # ============================
  Scenario: Validate pipeline completion
    Given all agents have completed
    When Agent 14 (QC) performs final validation
    Then qc_report.html is generated
    And at least 5 of 6 success criteria are met
    And the release recommendation is issued

  Scenario: Enforce model quality gate
    Given model_metrics.json exists
    When Agent 14 checks the best model ROC-AUC
    Then if ROC-AUC < 0.75, the status is CONDITIONAL
    And if ROC-AUC >= 0.75, the status is APPROVED

  # ============================
  # Security
  # ============================
  Scenario: Audit trail integrity
    Given the pipeline has run at least one agent
    When the audit trail at outputs/15_audit/audit_trail.jsonl is checked
    Then every entry has a timestamp
    And every entry has an agent_name
    And agent handoff messages have a checksum

  Scenario: Australian Privacy Act compliance
    Given the platform processes patient health data
    When data is stored or transmitted
    Then all PHI is encrypted at rest
    And all PII is anonymized in logs
    And access is logged per APP Principle 11
