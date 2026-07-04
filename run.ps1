# CVD Risk Intelligence Platform - Windows Run Script
# Usage:
#   .\run.ps1              ? full pipeline
#   .\run.ps1 -Agent 1    ? single agent
#   .\run.ps1 -From 1 -To 7 ? agents 1-7
#   .\run.ps1 -DryRun     ? dry run
#   .\run.ps1 -Test       ? run tests
#   .\run.ps1 -Status     ? show pipeline status

param(
    [int]$Agent = 0,
    [int]$From = 1,
    [int]$To = 15,
    [switch]$DryRun,
    [switch]$Test,
    [switch]$Status,
    [switch]$Security,
    [switch]$Help
)

$PYTHON = ".venv\Scripts\python.exe"
$PIP    = ".venv\Scripts\pip.exe"

if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: .venv not found. Run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

function Show-Banner {
    Write-Host ""
    Write-Host "[CVD RISK] CVD Risk Intelligence Platform" -ForegroundColor Cyan
    Write-Host "   15-Agent Pipeline | Australian Healthcare Compliant" -ForegroundColor DarkCyan
    Write-Host ""
}

# -- HELP -----------------------------------------------------
if ($Help) {
    Show-Banner
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1                  Run full pipeline (Agents 1-15)"
    Write-Host "  .\run.ps1 -Agent 6         Run Agent 6 (ML) only"
    Write-Host "  .\run.ps1 -From 4 -To 7   Run Agents 4-7"
    Write-Host "  .\run.ps1 -DryRun          Verify structure without executing"
    Write-Host "  .\run.ps1 -Test            Run test suite"
    Write-Host "  .\run.ps1 -Status          Show pipeline status"
    Write-Host "  .\run.ps1 -Security        Test Secure Vibe Framework"
    Write-Host ""
    Write-Host "INDIVIDUAL AGENTS:" -ForegroundColor Yellow
    Write-Host "  -Agent 1   Dataset Discovery"
    Write-Host "  -Agent 2   Data Cleaning"
    Write-Host "  -Agent 3   Preprocessing"
    Write-Host "  -Agent 4   EDA"
    Write-Host "  -Agent 5   Statistical Analysis"
    Write-Host "  -Agent 6   Machine Learning"
    Write-Host "  -Agent 7   Explainable AI (SHAP + LIME)"
    Write-Host "  -Agent 8   Graph Intelligence"
    Write-Host "  -Agent 9   Vector Database"
    Write-Host "  -Agent 10  RAG"
    Write-Host "  -Agent 11  Security Operations"
    Write-Host "  -Agent 12  Deployment"
    Write-Host "  -Agent 13  Guardrail"
    Write-Host "  -Agent 14  Quality Control"
    Write-Host "  -Agent 15  Code Review"
    exit 0
}

Show-Banner

# -- STATUS ----------------------------------------------------
if ($Status) {
    Write-Host "[STATUS] Pipeline Status" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan

    $agents = @(
        @{N=1;  Name="Dataset Discovery";     Output="outputs\01_data_catalog\dataset_catalog.json"},
        @{N=2;  Name="Data Cleaning";          Output="outputs\02_data_cleaning\cleaned_dataset.parquet"},
        @{N=3;  Name="Preprocessing";          Output="outputs\03_preprocessing\processed_dataset.parquet"},
        @{N=4;  Name="EDA";                    Output="outputs\04_eda\eda_report.html"},
        @{N=5;  Name="Statistical Analysis";   Output="outputs\05_statistics\statistical_report.html"},
        @{N=6;  Name="Machine Learning";       Output="outputs\06_machine_learning\metrics\model_metrics.json"},
        @{N=7;  Name="Explainable AI";         Output="outputs\07_xai\shap_report.html"},
        @{N=8;  Name="Graph Intelligence";     Output="outputs\08_graph_rag\knowledge_graph.json"},
        @{N=9;  Name="Vector Database";        Output="outputs\09_vector_db\vector_db_config.json"},
        @{N=10; Name="RAG";                    Output="outputs\10_rag\rag_config.json"},
        @{N=11; Name="Security Operations";    Output="outputs\11_security\security_audit.json"},
        @{N=12; Name="Deployment";             Output="outputs\12_deployment\deployment_architecture.json"},
        @{N=13; Name="Guardrail";              Output="outputs\11_security\guardrail_report.json"},
        @{N=14; Name="Quality Control";        Output="outputs\13_documentation\qc_report.html"},
        @{N=15; Name="Code Review";            Output="outputs\15_audit\code_review.json"}
    )

    foreach ($a in $agents) {
        $icon = "[ ]"
        if (Test-Path $a.Output) { $icon = "[x]" }
        Write-Host "  $icon Agent $($a.N): $($a.Name)"
    }

    Write-Host ""
    if (Test-Path "outputs\15_audit\audit_trail.jsonl") {
        $lines = (Get-Content "outputs\15_audit\audit_trail.jsonl" | Measure-Object -Line).Lines
        Write-Host "[AUDIT] Audit Trail: $lines entries" -ForegroundColor DarkGray
    }

    if (Test-Path "outputs\06_machine_learning\metrics\model_metrics.json") {
        $metrics = Get-Content "outputs\06_machine_learning\metrics\model_metrics.json" | ConvertFrom-Json
        $best = $metrics.best_model
        Write-Host ""
        Write-Host "[BEST] Best Model: $($best.model)" -ForegroundColor Green
        Write-Host "   ROC-AUC:    $($best.roc_auc)" -ForegroundColor Green
        Write-Host "   F1 Score:   $($best.f1_score)" -ForegroundColor Green
        Write-Host "   Sensitivity: $($best.sensitivity)" -ForegroundColor Green
    }
    exit 0
}

# -- TESTS -----------------------------------------------------
if ($Test) {
    Write-Host "[TEST] Running test suite..." -ForegroundColor Yellow
    & $PYTHON -m pytest tests/ -v --tb=short
    exit $LASTEXITCODE
}

# -- SECURITY FRAMEWORK TEST -----------------------------------
if ($Security) {
    Write-Host "[SECURE] Testing Secure Vibe Coding Framework..." -ForegroundColor Yellow
    & $PYTHON security\secure_vibe_framework.py
    exit $LASTEXITCODE
}

# -- SINGLE AGENT ----------------------------------------------
if ($Agent -gt 0) {
    $agentDirs = @{
        1  = "agents\01_discovery\agent.py"
        2  = "agents\02_cleaning\agent.py"
        3  = "agents\03_preprocessing\agent.py"
        4  = "agents\04_eda\agent.py"
        5  = "agents\05_statistics\agent.py"
        6  = "agents\06_ml\agent.py"
        7  = "agents\07_xai\agent.py"
        8  = "agents\08_graph\agent.py"
        9  = "agents\09_vector\agent.py"
        10 = "agents\10_rag\agent.py"
        11 = "agents\11_security\agent.py"
        12 = "agents\12_deployment\agent.py"
        13 = "agents\13_guardrail\agent.py"
        14 = "agents\14_qc\agent.py"
        15 = "agents\15_codereview\agent.py"
    }
    $agentNames = @{
        1="Dataset Discovery"; 2="Data Cleaning"; 3="Preprocessing";
        4="EDA"; 5="Statistical Analysis"; 6="Machine Learning";
        7="Explainable AI"; 8="Graph Intelligence"; 9="Vector Database";
        10="RAG"; 11="Security Operations"; 12="Deployment";
        13="Guardrail"; 14="Quality Control"; 15="Code Review"
    }

    if (-not $agentDirs.ContainsKey($Agent)) {
        Write-Host "ERROR: Agent $Agent not found (valid: 1-15)" -ForegroundColor Red
        exit 1
    }

    Write-Host "[RUNNING] Running Agent $Agent - $($agentNames[$Agent])" -ForegroundColor Cyan
    & $PYTHON $agentDirs[$Agent]
    exit $LASTEXITCODE
}

# -- DRY RUN ---------------------------------------------------
if ($DryRun) {
    Write-Host "[AUDIT] Dry run..." -ForegroundColor Yellow
    & $PYTHON orchestrator.py --dry-run
    exit $LASTEXITCODE
}

# -- PARTIAL PIPELINE ------------------------------------------
if ($From -ne 1 -or $To -ne 15) {
    Write-Host "[RUNNING] Running Agents $From ? $To" -ForegroundColor Cyan
    & $PYTHON orchestrator.py --from-agent $From --to-agent $To
    exit $LASTEXITCODE
}

# -- FULL PIPELINE ---------------------------------------------
Write-Host "[RUNNING] Running full 15-agent pipeline..." -ForegroundColor Cyan
Write-Host "   This will take several minutes depending on dataset size." -ForegroundColor DarkGray
Write-Host ""
& $PYTHON orchestrator.py
$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "[x] Pipeline completed successfully!" -ForegroundColor Green
    Write-Host "   Run '.\run.ps1 -Status' to see results." -ForegroundColor DarkGray
} else {
    Write-Host "[FAILED] Pipeline failed. Check logs above." -ForegroundColor Red
    Write-Host "   Run '.\run.ps1 -Status' to see which agents completed." -ForegroundColor DarkGray
}
exit $exitCode
