# CVD Risk Intelligence Platform — Windows Setup & Run Script
# Run from PowerShell (NOT Git Bash) as:
#   .\setup.ps1

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CVD Risk Intelligence Platform — Windows Setup    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Check Python ──────────────────────────────────────
Write-Host "[1/5] Checking Python version..." -ForegroundColor Yellow
$pyVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install from https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "      Found: $pyVersion" -ForegroundColor Green

# ── Step 2: Create virtual environment ───────────────────────
Write-Host "[2/5] Creating virtual environment (.venv)..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "      .venv already exists, skipping creation." -ForegroundColor DarkGray
} else {
    python -m venv .venv
    Write-Host "      .venv created." -ForegroundColor Green
}

# ── Step 3: Activate + upgrade pip ───────────────────────────
Write-Host "[3/5] Activating venv and upgrading pip..." -ForegroundColor Yellow
& ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
Write-Host "      pip upgraded." -ForegroundColor Green

# ── Step 4: Install dependencies ─────────────────────────────
Write-Host "[4/5] Installing dependencies (this takes 2-5 min)..." -ForegroundColor Yellow
& ".venv\Scripts\pip.exe" install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip install failed. Check requirements.txt" -ForegroundColor Red
    exit 1
}
Write-Host "      Dependencies installed." -ForegroundColor Green

# ── Step 5: Create dataset folder ────────────────────────────
Write-Host "[5/5] Creating dataset folder..." -ForegroundColor Yellow
$datasetDir = "cvd risk dataset"
if (-not (Test-Path $datasetDir)) {
    New-Item -ItemType Directory -Path $datasetDir | Out-Null
    Write-Host "      Created: '$datasetDir'" -ForegroundColor Green
} else {
    Write-Host "      '$datasetDir' already exists." -ForegroundColor DarkGray
}

# ── Create .env from template ─────────────────────────────────
if (-not (Test-Path ".env")) {
    Copy-Item ".env.template" ".env"
    Write-Host "      .env created from template." -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1. Copy your CVD dataset files into: '$datasetDir\'" -ForegroundColor White
Write-Host "  2. Run the pipeline:" -ForegroundColor White
Write-Host "       .venv\Scripts\python.exe orchestrator.py" -ForegroundColor Yellow
Write-Host "     OR use the run script:" -ForegroundColor White
Write-Host "       .\run.ps1" -ForegroundColor Yellow
Write-Host ""
