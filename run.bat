@echo off
REM CVD Risk Intelligence Platform — Windows Batch Runner
REM Works in CMD, Git Bash (via cmd), and PowerShell
REM Usage: run.bat [command] [agent_number]
REM
REM Commands:
REM   run.bat setup         → Setup virtual environment
REM   run.bat run           → Full pipeline
REM   run.bat agent 6       → Run specific agent (1-15)
REM   run.bat from 4 7      → Run agents 4 through 7
REM   run.bat test          → Run test suite
REM   run.bat status        → Show pipeline status
REM   run.bat dry           → Dry run

SET PYTHON=.venv\Scripts\python.exe
SET PIP=.venv\Scripts\pip.exe

IF "%1"=="" GOTO help
IF "%1"=="help" GOTO help
IF "%1"=="setup" GOTO setup
IF "%1"=="run" GOTO run
IF "%1"=="agent" GOTO agent
IF "%1"=="from" GOTO partial
IF "%1"=="test" GOTO test
IF "%1"=="status" GOTO status
IF "%1"=="dry" GOTO dryrun
IF "%1"=="security" GOTO security
IF "%1"=="guardrail" GOTO guardrail
IF "%1"=="qc" GOTO qc
GOTO help

REM ── SETUP ────────────────────────────────────────────
:setup
echo.
echo [1/4] Checking Python...
python --version
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Install from https://python.org
    exit /b 1
)

echo [2/4] Creating virtual environment...
IF NOT EXIST ".venv" (
    python -m venv .venv
    echo .venv created.
) ELSE (
    echo .venv already exists, skipping.
)

echo [3/4] Upgrading pip...
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet

echo [4/4] Installing dependencies (2-5 min)...
.venv\Scripts\pip.exe install -r requirements.txt
IF ERRORLEVEL 1 (
    echo ERROR: pip install failed.
    exit /b 1
)

IF NOT EXIST "cvd risk dataset" mkdir "cvd risk dataset"
IF NOT EXIST ".env" copy ".env.template" ".env" >nul

echo.
echo Setup complete!
echo Place your CVD data files in: "cvd risk dataset\"
echo Then run: run.bat run
GOTO end

REM ── FULL PIPELINE ─────────────────────────────────────
:run
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Running full 15-agent pipeline...
%PYTHON% orchestrator.py
GOTO end

REM ── SINGLE AGENT ──────────────────────────────────────
:agent
IF "%2"=="" (
    echo Usage: run.bat agent [1-15]
    exit /b 1
)
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
SET AGENT_MAP_1=agents\01_discovery\agent.py
SET AGENT_MAP_2=agents\02_cleaning\agent.py
SET AGENT_MAP_3=agents\03_preprocessing\agent.py
SET AGENT_MAP_4=agents\04_eda\agent.py
SET AGENT_MAP_5=agents\05_statistics\agent.py
SET AGENT_MAP_6=agents\06_ml\agent.py
SET AGENT_MAP_7=agents\07_xai\agent.py
SET AGENT_MAP_8=agents\08_graph\agent.py
SET AGENT_MAP_9=agents\09_vector\agent.py
SET AGENT_MAP_10=agents\10_rag\agent.py
SET AGENT_MAP_11=agents\11_security\agent.py
SET AGENT_MAP_12=agents\12_deployment\agent.py
SET AGENT_MAP_13=agents\13_guardrail\agent.py
SET AGENT_MAP_14=agents\14_qc\agent.py
SET AGENT_MAP_15=agents\15_codereview\agent.py

SET AGENT_PATH=AGENT_MAP_%2
echo Running Agent %2...
%PYTHON% !%AGENT_PATH%!
GOTO end

REM ── PARTIAL PIPELINE ──────────────────────────────────
:partial
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Running Agents %2 through %3...
%PYTHON% orchestrator.py --from-agent %2 --to-agent %3
GOTO end

REM ── DRY RUN ───────────────────────────────────────────
:dryrun
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Dry run - verifying structure...
%PYTHON% orchestrator.py --dry-run
GOTO end

REM ── TESTS ─────────────────────────────────────────────
:test
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Running test suite...
%PYTHON% -m pytest tests\ -v --tb=short
GOTO end

REM ── SECURITY ──────────────────────────────────────────
:security
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Testing Secure Vibe Coding Framework...
%PYTHON% security\secure_vibe_framework.py
GOTO end

REM ── GUARDRAIL ─────────────────────────────────────────
:guardrail
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Running Guardrail Agent...
%PYTHON% agents\13_guardrail\agent.py
GOTO end

REM ── QC ────────────────────────────────────────────────
:qc
IF NOT EXIST %PYTHON% (
    echo ERROR: Run 'run.bat setup' first.
    exit /b 1
)
echo Running Quality Control Agent...
%PYTHON% agents\14_qc\agent.py
GOTO end

REM ── STATUS ────────────────────────────────────────────
:status
echo.
echo CVD Platform - Pipeline Status
echo ================================
IF EXIST "outputs\01_data_catalog\dataset_catalog.json"           (echo [OK] Agent  1: Dataset Discovery) ELSE (echo [--] Agent  1: Dataset Discovery)
IF EXIST "outputs\02_data_cleaning\cleaned_dataset.parquet"       (echo [OK] Agent  2: Data Cleaning) ELSE (echo [--] Agent  2: Data Cleaning)
IF EXIST "outputs\03_preprocessing\processed_dataset.parquet"     (echo [OK] Agent  3: Preprocessing) ELSE (echo [--] Agent  3: Preprocessing)
IF EXIST "outputs\04_eda\eda_report.html"                         (echo [OK] Agent  4: EDA) ELSE (echo [--] Agent  4: EDA)
IF EXIST "outputs\05_statistics\statistical_report.html"          (echo [OK] Agent  5: Statistical Analysis) ELSE (echo [--] Agent  5: Statistical Analysis)
IF EXIST "outputs\06_machine_learning\metrics\model_metrics.json" (echo [OK] Agent  6: Machine Learning) ELSE (echo [--] Agent  6: Machine Learning)
IF EXIST "outputs\07_xai\shap_report.html"                        (echo [OK] Agent  7: Explainable AI) ELSE (echo [--] Agent  7: Explainable AI)
IF EXIST "outputs\08_graph_rag\knowledge_graph.json"              (echo [OK] Agent  8: Graph Intelligence) ELSE (echo [--] Agent  8: Graph Intelligence)
IF EXIST "outputs\09_vector_db\vector_db_config.json"             (echo [OK] Agent  9: Vector Database) ELSE (echo [--] Agent  9: Vector Database)
IF EXIST "outputs\10_rag\rag_config.json"                         (echo [OK] Agent 10: RAG) ELSE (echo [--] Agent 10: RAG)
IF EXIST "outputs\11_security\security_audit.json"                (echo [OK] Agent 11: Security Operations) ELSE (echo [--] Agent 11: Security Operations)
IF EXIST "outputs\12_deployment\deployment_architecture.json"     (echo [OK] Agent 12: Deployment) ELSE (echo [--] Agent 12: Deployment)
IF EXIST "outputs\11_security\guardrail_report.json"              (echo [OK] Agent 13: Guardrail) ELSE (echo [--] Agent 13: Guardrail)
IF EXIST "outputs\13_documentation\qc_report.html"                (echo [OK] Agent 14: Quality Control) ELSE (echo [--] Agent 14: Quality Control)
IF EXIST "outputs\15_audit\code_review.json"                      (echo [OK] Agent 15: Code Review) ELSE (echo [--] Agent 15: Code Review)
echo.
IF EXIST "outputs\15_audit\audit_trail.jsonl" echo Audit trail exists.
GOTO end

REM ── HELP ──────────────────────────────────────────────
:help
echo.
echo CVD Risk Intelligence Platform — Windows Runner
echo ================================================
echo.
echo USAGE:
echo   run.bat setup          Setup virtual environment + dependencies
echo   run.bat run            Run full 15-agent pipeline
echo   run.bat agent [1-15]   Run a specific agent
echo   run.bat from [N] [M]   Run agents N through M
echo   run.bat dry            Dry run (structure check only)
echo   run.bat test           Run test suite
echo   run.bat status         Show which agents have completed
echo   run.bat security       Test Secure Vibe Coding Framework
echo   run.bat guardrail      Run Guardrail Agent only
echo   run.bat qc             Run Quality Control Agent only
echo.
echo EXAMPLES:
echo   run.bat setup
echo   run.bat run
echo   run.bat agent 6        (just Machine Learning)
echo   run.bat from 1 7       (Discovery through XAI)
echo   run.bat status

:end
