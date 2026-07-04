#!/usr/bin/env bash
# CVD Risk Intelligence Platform — Git Bash / WSL Runner
# Works in: Git Bash, WSL, PowerShell with bash, macOS, Linux
#
# Usage:
#   bash run.sh setup
#   bash run.sh run
#   bash run.sh agent 6
#   bash run.sh from 1 7
#   bash run.sh test
#   bash run.sh status

set -euo pipefail

# Detect Windows vs Unix python path
if [[ -f ".venv/Scripts/python.exe" ]]; then
    PYTHON=".venv/Scripts/python.exe"
    PIP=".venv/Scripts/pip.exe"
    PYTEST=".venv/Scripts/pytest.exe"
elif [[ -f ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"
    PIP=".venv/bin/pip"
    PYTEST=".venv/bin/pytest"
else
    PYTHON="python"
    PIP="pip"
    PYTEST="python -m pytest"
fi

COMMAND="${1:-help}"

# ── Colours ──────────────────────────────────────────────────
GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'
RED='\033[0;31m'; GRAY='\033[0;37m'; RESET='\033[0m'
BOLD='\033[1m'

banner() {
    echo -e "\n${CYAN}${BOLD}🏥 CVD Risk Intelligence Platform${RESET}"
    echo -e "${CYAN}   15-Agent Pipeline | Australian Healthcare Compliant${RESET}\n"
}

check_venv() {
    if [[ ! -f "$PYTHON" ]] && [[ "$PYTHON" != "python" ]]; then
        echo -e "${RED}ERROR: .venv not found. Run: bash run.sh setup${RESET}"
        exit 1
    fi
}

# ── SETUP ─────────────────────────────────────────────────────
setup() {
    banner
    echo -e "${YELLOW}[1/5] Checking Python...${RESET}"
    python --version || { echo -e "${RED}ERROR: Python not found${RESET}"; exit 1; }

    echo -e "${YELLOW}[2/5] Creating virtual environment...${RESET}"
    if [[ ! -d ".venv" ]]; then
        python -m venv .venv
        echo -e "${GREEN}      .venv created${RESET}"
    else
        echo -e "${GRAY}      .venv already exists${RESET}"
    fi

    echo -e "${YELLOW}[3/5] Upgrading pip...${RESET}"
    $PYTHON -m pip install --upgrade pip --quiet

    echo -e "${YELLOW}[4/5] Installing core dependencies...${RESET}"
    $PIP install -r requirements.txt

    echo -e "${YELLOW}[5/5] Creating project folders...${RESET}"
    mkdir -p "cvd risk dataset"
    [[ ! -f ".env" ]] && cp .env.template .env && echo -e "${GREEN}      .env created${RESET}"

    echo -e "\n${GREEN}${BOLD}✅ Setup complete!${RESET}"
    echo -e "  → Put your CVD data in: ${YELLOW}\"cvd risk dataset/\"${RESET}"
    echo -e "  → Then run: ${YELLOW}bash run.sh run${RESET}\n"
}

# ── RUN FULL PIPELINE ─────────────────────────────────────────
run_full() {
    check_venv; banner
    echo -e "${CYAN}🚀 Running full 15-agent pipeline...${RESET}\n"
    $PYTHON orchestrator.py
}

# ── SINGLE AGENT ──────────────────────────────────────────────
run_agent() {
    check_venv
    local n="${1:-0}"
    local -A agent_map=(
        [1]="agents/01_discovery/agent.py"
        [2]="agents/02_cleaning/agent.py"
        [3]="agents/03_preprocessing/agent.py"
        [4]="agents/04_eda/agent.py"
        [5]="agents/05_statistics/agent.py"
        [6]="agents/06_ml/agent.py"
        [7]="agents/07_xai/agent.py"
        [8]="agents/08_graph/agent.py"
        [9]="agents/09_vector/agent.py"
        [10]="agents/10_rag/agent.py"
        [11]="agents/11_security/agent.py"
        [12]="agents/12_deployment/agent.py"
        [13]="agents/13_guardrail/agent.py"
        [14]="agents/14_qc/agent.py"
        [15]="agents/15_codereview/agent.py"
    )
    local -A agent_names=(
        [1]="Dataset Discovery" [2]="Data Cleaning" [3]="Preprocessing"
        [4]="EDA" [5]="Statistical Analysis" [6]="Machine Learning"
        [7]="Explainable AI" [8]="Graph Intelligence" [9]="Vector Database"
        [10]="RAG" [11]="Security Operations" [12]="Deployment"
        [13]="Guardrail" [14]="Quality Control" [15]="Code Review"
    )
    if [[ -z "${agent_map[$n]+_}" ]]; then
        echo -e "${RED}ERROR: Agent $n not found (valid: 1-15)${RESET}"; exit 1
    fi
    echo -e "${CYAN}🤖 Agent $n: ${agent_names[$n]}${RESET}"
    $PYTHON "${agent_map[$n]}"
}

# ── PARTIAL PIPELINE ──────────────────────────────────────────
run_partial() {
    check_venv
    local from="${1:-1}" to="${2:-15}"
    echo -e "${CYAN}🚀 Running Agents $from → $to${RESET}"
    $PYTHON orchestrator.py --from-agent "$from" --to-agent "$to"
}

# ── DRY RUN ───────────────────────────────────────────────────
dry_run() {
    check_venv
    echo -e "${YELLOW}📋 Dry run...${RESET}"
    $PYTHON orchestrator.py --dry-run
}

# ── TESTS ─────────────────────────────────────────────────────
run_tests() {
    check_venv
    echo -e "${YELLOW}🧪 Running test suite...${RESET}"
    $PYTHON -m pytest tests/ -v --tb=short
}

run_tests_unit() {
    check_venv
    echo -e "${YELLOW}🧪 Unit tests...${RESET}"
    $PYTHON -m pytest tests/test_agents.py -v --tb=short
}

run_tests_security() {
    check_venv
    echo -e "${YELLOW}🔐 Security tests...${RESET}"
    $PYTHON -m pytest tests/test_agents.py::TestSecureVibeFramework -v
}

# ── SECURITY FRAMEWORK ────────────────────────────────────────
test_security_framework() {
    check_venv
    echo -e "${YELLOW}🔒 Testing Secure Vibe Coding Framework...${RESET}"
    $PYTHON security/secure_vibe_framework.py
}

# ── STATUS ────────────────────────────────────────────────────
show_status() {
    banner
    echo -e "${BOLD}📊 Pipeline Status${RESET}"
    echo   "=================="

    declare -A outputs=(
        [1]="outputs/01_data_catalog/dataset_catalog.json"
        [2]="outputs/02_data_cleaning/cleaned_dataset.parquet"
        [3]="outputs/03_preprocessing/processed_dataset.parquet"
        [4]="outputs/04_eda/eda_report.html"
        [5]="outputs/05_statistics/statistical_report.html"
        [6]="outputs/06_machine_learning/metrics/model_metrics.json"
        [7]="outputs/07_xai/shap_report.html"
        [8]="outputs/08_graph_rag/knowledge_graph.json"
        [9]="outputs/09_vector_db/vector_db_config.json"
        [10]="outputs/10_rag/rag_config.json"
        [11]="outputs/11_security/security_audit.json"
        [12]="outputs/12_deployment/deployment_architecture.json"
        [13]="outputs/11_security/guardrail_report.json"
        [14]="outputs/13_documentation/qc_report.html"
        [15]="outputs/15_audit/code_review.json"
    )
    declare -A names=(
        [1]="Dataset Discovery" [2]="Data Cleaning" [3]="Preprocessing"
        [4]="EDA" [5]="Statistical Analysis" [6]="Machine Learning"
        [7]="Explainable AI" [8]="Graph Intelligence" [9]="Vector Database"
        [10]="RAG" [11]="Security Operations" [12]="Deployment"
        [13]="Guardrail" [14]="Quality Control" [15]="Code Review"
    )

    for n in $(seq 1 15); do
        path="${outputs[$n]}"
        name="${names[$n]}"
        if [[ -f "$path" ]]; then
            printf "  ${GREEN}✅${RESET} Agent %2d: %s\n" "$n" "$name"
        else
            printf "  ${GRAY}⬜${RESET} Agent %2d: %s\n" "$n" "$name"
        fi
    done

    echo ""
    if [[ -f "outputs/15_audit/audit_trail.jsonl" ]]; then
        lines=$(wc -l < "outputs/15_audit/audit_trail.jsonl")
        echo -e "${GRAY}📋 Audit Trail: $lines entries${RESET}"
    fi

    if [[ -f "outputs/06_machine_learning/metrics/model_metrics.json" ]]; then
        echo -e "\n${GREEN}${BOLD}🏆 Best Model Results:${RESET}"
        $PYTHON -c "
import json
with open('outputs/06_machine_learning/metrics/model_metrics.json') as f:
    d = json.load(f)
b = d.get('best_model', {})
print(f\"   Model:       {b.get('model','N/A')}\")
print(f\"   ROC-AUC:     {b.get('roc_auc','N/A')}\")
print(f\"   F1 Score:    {b.get('f1_score','N/A')}\")
print(f\"   Sensitivity: {b.get('sensitivity','N/A')}\")
print(f\"   Specificity: {b.get('specificity','N/A')}\")
" 2>/dev/null || true
    fi
    echo ""
}

# ── HELP ──────────────────────────────────────────────────────
show_help() {
    banner
    echo -e "${BOLD}USAGE:${RESET}"
    echo "  bash run.sh setup            Setup venv + install dependencies"
    echo "  bash run.sh run              Run full 15-agent pipeline"
    echo "  bash run.sh agent [1-15]     Run a specific agent"
    echo "  bash run.sh from [N] [M]     Run agents N through M"
    echo "  bash run.sh dry              Dry run (structure check)"
    echo "  bash run.sh test             Full test suite"
    echo "  bash run.sh test-unit        Unit tests only"
    echo "  bash run.sh test-security    Security framework tests"
    echo "  bash run.sh security         Test Secure Vibe Framework"
    echo "  bash run.sh status           Show pipeline status"
    echo ""
    echo -e "${BOLD}QUICK START:${RESET}"
    echo "  bash run.sh setup"
    echo "  # copy your CVD data to: 'cvd risk dataset/'"
    echo "  bash run.sh run"
    echo ""
    echo -e "${BOLD}COMMON WORKFLOWS:${RESET}"
    echo "  bash run.sh agent 1          # discover dataset"
    echo "  bash run.sh from 1 3         # data pipeline only"
    echo "  bash run.sh from 4 7         # ML pipeline only"
    echo "  bash run.sh agent 13         # guardrail check"
    echo "  bash run.sh agent 14         # QC report"
    echo ""
}

# ── DISPATCH ──────────────────────────────────────────────────
case "$COMMAND" in
    setup)          setup ;;
    run)            run_full ;;
    agent)          run_agent "${2:-0}" ;;
    from)           run_partial "${2:-1}" "${3:-15}" ;;
    dry)            dry_run ;;
    test)           run_tests ;;
    test-unit)      run_tests_unit ;;
    test-security)  run_tests_security ;;
    security)       test_security_framework ;;
    status)         show_status ;;
    api)            start_api ;;
    dashboard)      start_dashboard ;;
    serve)          start_all_services ;;
    help|--help|-h) show_help ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${RESET}"
        show_help
        exit 1
        ;;
esac

# ── API SERVER ────────────────────────────────────────────────
start_api() {
    check_venv
    echo -e "${CYAN}🚀 Starting FastAPI server on http://localhost:8000${RESET}"
    echo -e "${GRAY}   API docs: http://localhost:8000/docs${RESET}"
    echo -e "${GRAY}   Press Ctrl+C to stop${RESET}\n"
    $PYTHON -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
}

# ── STREAMLIT DASHBOARD ───────────────────────────────────────
start_dashboard() {
    check_venv
    echo -e "${CYAN}🏥 Starting Streamlit Clinical Dashboard on http://localhost:8501${RESET}"
    echo -e "${GRAY}   Press Ctrl+C to stop${RESET}\n"
    $PYTHON -m streamlit run dashboard.py \
        --server.port 8501 \
        --server.address localhost \
        --browser.gatherUsageStats false
}

# ── BOTH ─────────────────────────────────────────────────────
start_all_services() {
    check_venv
    echo -e "${CYAN}🚀 Starting all services...${RESET}"
    echo -e "   API:       ${YELLOW}http://localhost:8000${RESET}"
    echo -e "   API Docs:  ${YELLOW}http://localhost:8000/docs${RESET}"
    echo -e "   Dashboard: ${YELLOW}http://localhost:8501${RESET}"
    echo -e "${GRAY}   Starting API in background, dashboard in foreground${RESET}\n"
    $PYTHON -m uvicorn api:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    sleep 2
    $PYTHON -m streamlit run dashboard.py --server.port 8501 \
        --browser.gatherUsageStats false
    kill $API_PID 2>/dev/null
}

