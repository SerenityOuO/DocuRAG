Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment not found at $venvPython. Run scripts/test-backend.ps1 first."
}

Write-Host "Observability smoke"
Write-Host "Backend: $backendRoot"

Push-Location $backendRoot
try {
    & $venvPython -m pytest tests/test_observability.py -q
    if ($LASTEXITCODE -ne 0) {
        throw "Observability pytest smoke failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$requiredText = @(
    "Loki",
    "Grafana",
    "OpenSearch",
    "api_request",
    "rag_trace",
    "eval_metrics",
    "worker_log",
    "trace_id",
    "request_id",
    "log schema",
    "opt-in",
    "API p95 latency",
    "API error rate",
    "Worker task failures",
    "RAG retrieval latency",
    "RAG rerank latency",
    "RAG generation latency",
    "Fallback count",
    "Hit Rate",
    "MRR"
)

$searchTargets = @(
    (Join-Path $repoRoot "backend"),
    (Join-Path $repoRoot "infra"),
    (Join-Path $repoRoot "docs"),
    (Join-Path $repoRoot "scripts"),
    (Join-Path $repoRoot "README_DEV.md"),
    (Join-Path $repoRoot "TODO.md"),
    (Join-Path $repoRoot "tasks/phase-39-deployment-observability-finetuning")
)

foreach ($text in $requiredText) {
    & rg -n --fixed-strings $text @searchTargets | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Expected observability text '$text' was not found."
    }
}

Write-Host "Observability smoke passed."
