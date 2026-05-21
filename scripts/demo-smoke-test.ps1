param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($SamplePath)) {
    $SamplePath = Join-Path $repoRoot "sample-data/documents/mock-invoice-aurora.txt"
}

$resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

Write-Host "Demo smoke test"
Write-Host "API: $ApiBaseUrl"

$health = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/health"
Assert-Condition ($health.status -eq "ok") "Expected /health status ok."
Assert-Condition ($health.version -eq "0.5.1") "Expected /health version 0.5.1."
Write-Host "Health OK: version $($health.version)"

$uploadRaw = & curl.exe -sS -X POST "$ApiBaseUrl/documents/upload" -F "file=@$resolvedSamplePath;type=text/plain"
if ($LASTEXITCODE -ne 0) {
    throw "Upload failed with exit code $LASTEXITCODE"
}

$upload = $uploadRaw | ConvertFrom-Json
Assert-Condition (-not [string]::IsNullOrWhiteSpace($upload.document_id)) "Upload did not return document_id."
Assert-Condition ($upload.filename -eq "mock-invoice-aurora.txt") "Upload returned unexpected filename."
Write-Host "Upload OK: $($upload.document_id)"

$ocr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/ocr/mock"
Assert-Condition ($ocr.status -eq "completed") "OCR mock did not complete."
Assert-Condition ($ocr.text -match "AUR-2026-051") "OCR mock did not include sample invoice content."
Write-Host "OCR mock OK"

$ragBody = @{
    query = "payment due date Net 15"
    top_k = 3
} | ConvertTo-Json
$rag = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/rag/query" -ContentType "application/json" -Body $ragBody

Assert-Condition ($rag.answer -match "mock-invoice-aurora.txt") "RAG answer did not reference the sample invoice."
Assert-Condition ($rag.citations.Count -gt 0) "RAG did not return citations."
Assert-Condition ($rag.retrieved_chunks.Count -gt 0) "RAG did not return retrieved chunks."
Assert-Condition (($rag.retrieved_chunks | ConvertTo-Json -Depth 8) -match "AUR-2026-051") "Retrieved chunks did not include expected invoice evidence."
Write-Host "RAG query OK"

Write-Host "Demo smoke test passed."
