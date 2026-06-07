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
        tests/test_vector_indexing.py `
        tests/test_vector_store.py `
        tests/test_documents.py `
        tests/test_rag.py `
        -q `
        -k "semantic_chunking or payload_indexes or filter_to_tenant_project_document_and_source or cleanup_stale_points or project_vector_reindex or project_filter_for_project_scoped_documents"
    if ($LASTEXITCODE -ne 0) {
        throw "Indexing quality smoke failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

Write-Host "Indexing quality smoke passed."
