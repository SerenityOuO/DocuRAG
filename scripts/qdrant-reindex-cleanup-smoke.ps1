Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$pythonPath = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonPath)) {
    throw "Backend virtualenv was not found at $pythonPath. Run backend setup before this smoke script."
}

Push-Location $backendRoot
try {
    & $pythonPath -m pytest `
        tests/test_vector_store.py `
        tests/test_vector_indexing.py `
        tests/test_documents.py `
        -q `
        -k "payload_index or cleanup or reindex"
    if ($LASTEXITCODE -ne 0) {
        throw "Qdrant reindex / cleanup smoke failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Host "Qdrant reindex / cleanup smoke passed."
