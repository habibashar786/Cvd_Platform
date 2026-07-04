# CVD Risk Intelligence Platform — Makefile
# Usage: make <target>

.PHONY: all setup run test clean status help

PYTHON := python
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

setup:
	@echo "🔧 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Setup complete. Activate with: source .venv/bin/activate"

install-core:
	pip install pandas numpy pyarrow scikit-learn catboost xgboost lightgbm \
	            imbalanced-learn shap lime plotly scipy statsmodels \
	            structlog pydantic python-dotenv networkx

# ─────────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────────

run:
	@echo "🚀 Running full 15-agent CVD pipeline..."
	$(PYTHON) orchestrator.py

run-dry:
	@echo "📋 Dry run — verifying structure..."
	$(PYTHON) orchestrator.py --dry-run

agent-1:
	@echo "🔍 Agent 1: Dataset Discovery"
	$(PYTHON) agents/01_discovery/agent.py

agent-2:
	@echo "🧹 Agent 2: Data Cleaning"
	$(PYTHON) agents/02_cleaning/agent.py

agent-3:
	@echo "⚙️  Agent 3: Preprocessing"
	$(PYTHON) agents/03_preprocessing/agent.py

agent-4:
	@echo "📊 Agent 4: EDA"
	$(PYTHON) agents/04_eda/agent.py

agent-5:
	@echo "📐 Agent 5: Statistical Analysis"
	$(PYTHON) agents/05_statistics/agent.py

agent-6:
	@echo "🤖 Agent 6: Machine Learning"
	$(PYTHON) agents/06_ml/agent.py

agent-7:
	@echo "🧠 Agent 7: Explainable AI"
	$(PYTHON) agents/07_xai/agent.py

agent-8:
	@echo "🕸️  Agent 8: Graph Intelligence"
	$(PYTHON) agents/08_graph/agent.py

agent-9:
	@echo "🗃️  Agent 9: Vector Database"
	$(PYTHON) agents/09_vector/agent.py

agent-10:
	@echo "💬 Agent 10: RAG"
	$(PYTHON) agents/10_rag/agent.py

agent-11:
	@echo "🔐 Agent 11: Security Ops"
	$(PYTHON) agents/11_security/agent.py

agent-12:
	@echo "🚢 Agent 12: Deployment"
	$(PYTHON) agents/12_deployment/agent.py

agent-13:
	@echo "🛡️  Agent 13: Guardrail"
	$(PYTHON) agents/13_guardrail/agent.py

agent-14:
	@echo "✅ Agent 14: Quality Control"
	$(PYTHON) agents/14_qc/agent.py

agent-15:
	@echo "👁️  Agent 15: Code Review"
	$(PYTHON) agents/15_codereview/agent.py

security-framework:
	@echo "🔒 Testing Secure Vibe Coding Framework..."
	$(PYTHON) security/secure_vibe_framework.py

# ─────────────────────────────────────────────
# TESTING
# ─────────────────────────────────────────────

test:
	@echo "🧪 Running full test suite..."
	pytest tests/ -v --tb=short

test-unit:
	@echo "🧪 Unit tests only..."
	pytest tests/test_agents.py -v

test-bdd:
	@echo "🥒 BDD scenario tests..."
	pytest tests/test_steps.py -v

test-security:
	@echo "🔐 Security tests..."
	pytest tests/test_agents.py::TestSecureVibeFramework -v

test-coverage:
	@echo "📊 Test coverage report..."
	pytest tests/ --cov=agents --cov=security --cov-report=html:outputs/14_tests/coverage_html
	@echo "Coverage report: outputs/14_tests/coverage_html/index.html"

# ─────────────────────────────────────────────
# QUALITY
# ─────────────────────────────────────────────

lint:
	@echo "🔍 Running linters..."
	ruff check agents/ security/ orchestrator.py
	black --check agents/ security/ orchestrator.py

format:
	@echo "✨ Formatting code..."
	black agents/ security/ orchestrator.py
	ruff check --fix agents/ security/

typecheck:
	@echo "🔬 Type checking..."
	mypy agents/ security/ --ignore-missing-imports

# ─────────────────────────────────────────────
# STATUS & AUDIT
# ─────────────────────────────────────────────

status:
	@echo "\n📊 CVD Platform — Pipeline Status"
	@echo "=================================="
	@echo "\n📁 Output Artifacts:"
	@find outputs/ -name "*.parquet" -o -name "*.html" -o -name "*.json" -o -name "*.pkl" \
	    2>/dev/null | sort | head -30
	@echo "\n📋 Audit Trail (last 10 entries):"
	@tail -10 outputs/15_audit/audit_trail.jsonl 2>/dev/null || echo "No audit trail yet"
	@echo "\n🔐 Security Events:"
	@wc -l outputs/15_audit/security_events.jsonl 2>/dev/null || echo "No security events yet"

audit:
	@echo "📋 Full audit trail:"
	@cat outputs/15_audit/audit_trail.jsonl 2>/dev/null | python -m json.tool 2>/dev/null \
	    || cat outputs/15_audit/audit_trail.jsonl 2>/dev/null || echo "No audit trail found"

qc-report:
	@echo "✅ QC Report:"
	@cat outputs/13_documentation/qc_report.json 2>/dev/null | python -m json.tool \
	    || echo "Run 'make agent-14' first"

# ─────────────────────────────────────────────
# MAINTENANCE
# ─────────────────────────────────────────────

clean-outputs:
	@echo "🗑️  Cleaning outputs (preserving audit trail)..."
	@find outputs/ -type f \
	    ! -path "outputs/15_audit/*" \
	    -name "*.parquet" -o -name "*.pkl" -o -name "*.html" -o -name "*.json" \
	    | xargs rm -f 2>/dev/null || true
	@echo "✅ Outputs cleaned (audit trail preserved)"

clean-all:
	@echo "⚠️  Cleaning ALL outputs including audit trail..."
	@rm -rf outputs/
	@echo "✅ Full clean complete"

# ─────────────────────────────────────────────
# HELP
# ─────────────────────────────────────────────

help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════╗"
	@echo "║   CVD Risk Intelligence Platform — Makefile Help    ║"
	@echo "╚══════════════════════════════════════════════════════╝"
	@echo ""
	@echo "SETUP:"
	@echo "  make setup          Create venv + install all dependencies"
	@echo "  make install-core   Quick install of core packages"
	@echo ""
	@echo "PIPELINE:"
	@echo "  make run            Run full 15-agent pipeline"
	@echo "  make run-dry        Dry run (verify structure)"
	@echo "  make agent-N        Run specific agent (1-15)"
	@echo "  make security-framework  Test Secure Vibe Framework"
	@echo ""
	@echo "TESTING:"
	@echo "  make test           Full test suite"
	@echo "  make test-unit      Unit tests only"
	@echo "  make test-bdd       BDD scenarios"
	@echo "  make test-security  Security framework tests"
	@echo "  make test-coverage  Coverage report"
	@echo ""
	@echo "QUALITY:"
	@echo "  make lint           Ruff + black check"
	@echo "  make format         Auto-format code"
	@echo "  make typecheck      mypy type checking"
	@echo ""
	@echo "STATUS:"
	@echo "  make status         Pipeline status overview"
	@echo "  make audit          View full audit trail"
	@echo "  make qc-report      View QC report"
	@echo ""
	@echo "MAINTENANCE:"
	@echo "  make clean-outputs  Clean outputs (keep audit)"
	@echo "  make clean-all      Full clean"
	@echo ""
