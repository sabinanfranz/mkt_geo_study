# dev.ps1 — MVP 로컬 개발 서버 시작 (Windows PowerShell)
#
# 사용법:
#   powershell -ExecutionPolicy Bypass -File scripts/dev.ps1            # 기본 포트 8000
#   powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Port 3000 # 커스텀 포트
#   $env:PORT=5000; powershell -ExecutionPolicy Bypass -File scripts/dev.ps1  # 환경변수

param(
    [int]$Port = 0
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot

# 우선순위: 파라미터 > 환경변수 > 기본값(8000)
if ($Port -eq 0) {
    if ($env:PORT) { $Port = [int]$env:PORT }
    else { $Port = 8000 }
}

Push-Location $ROOT

try {
    # 1. 가상환경 생성 (없으면)
    if (-not (Test-Path ".venv")) {
        Write-Host "[1/4] Creating .venv..." -ForegroundColor Cyan
        python -m venv .venv
    } else {
        Write-Host "[1/4] .venv already exists" -ForegroundColor Green
    }

    # 2. 패키지 설치
    Write-Host "[2/4] Installing dependencies..." -ForegroundColor Cyan
    & .venv\Scripts\pip install -q -r requirements.txt

    # 3. DB 초기화 + 시드
    Write-Host "[3/4] Running DB migrate + seed..." -ForegroundColor Cyan
    & .venv\Scripts\python scripts/db_seed.py

    # 4. 서버 시작
    Write-Host "[4/4] Starting uvicorn on http://127.0.0.1:$Port ..." -ForegroundColor Cyan
    & .venv\Scripts\uvicorn apps.api.main:app --reload --host 127.0.0.1 --port $Port
}
finally {
    Pop-Location
}
