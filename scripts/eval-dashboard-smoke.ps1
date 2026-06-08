Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment not found at $venvPython. Run scripts/test-backend.ps1 first."
}

Write-Host "Eval dashboard smoke"
Write-Host "Backend: $backendRoot"

Push-Location $backendRoot
try {
    & $venvPython -m pytest `
        tests/test_evaluation_api.py `
        tests/test_evaluation.py `
        tests/test_repositories.py `
        -q `
        -k "strategy_comparison or hybrid_rerank or local_json_repository_persists_eval_dataset_items_and_runs"
    if ($LASTEXITCODE -ne 0) {
        throw "Eval dashboard pytest smoke failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$requiredText = @(
    "strategy comparison",
    "hybrid_rerank",
    "rerank score",
    "failure cases",
    "fallback cases",
    "Recall"
)

$searchTargets = @(
    (Join-Path $repoRoot "backend"),
    (Join-Path $repoRoot "frontend"),
    (Join-Path $repoRoot "docs"),
    (Join-Path $repoRoot "TODO.md"),
    (Join-Path $repoRoot "tasks/phase-36-eval-dashboard-rerank-analysis")
)

foreach ($text in $requiredText) {
    & rg -n --fixed-strings $text @searchTargets | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Expected eval dashboard text '$text' was not found."
    }
}

Write-Host "Eval dashboard smoke passed."
