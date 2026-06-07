Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment not found. Run scripts/test-backend.ps1 first."
}

Push-Location $backendRoot
try {
    & $venvPython -m pytest tests/test_documents.py -q -k "page_images_for_scanned_pdf or merges_mixed_pdf_text_and_page_image_chunks or retries_page_images"
    if ($LASTEXITCODE -ne 0) {
        throw "Scanned PDF OCR smoke failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
