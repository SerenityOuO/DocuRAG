Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"
$smokeDataDir = Join-Path $repoRoot ".tmp/nats-worker-smoke"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment was not found. Run scripts/test-backend.ps1 first."
}

Push-Location $backendRoot
try {
    & $venvPython -m workers.skeleton --smoke --data-dir $smokeDataDir
    if ($LASTEXITCODE -ne 0) {
        throw "NATS worker smoke failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
