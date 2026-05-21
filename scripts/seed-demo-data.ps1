param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = "",
    [string]$Query = "payment due date Net 15",
    [int]$TopK = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($SamplePath)) {
    $SamplePath = Join-Path $repoRoot "sample-data/documents/mock-invoice-aurora.txt"
}

$resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path

Write-Host "DocuRAG demo seed"
Write-Host "API: $ApiBaseUrl"
Write-Host "Sample: $resolvedSamplePath"
Write-Host "Query: $Query"

$health = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/health"
Write-Host "Health: $($health.status), version $($health.version)"

$uploadRaw = & curl.exe -sS -X POST "$ApiBaseUrl/documents/upload" -F "file=@$resolvedSamplePath;type=text/plain"
if ($LASTEXITCODE -ne 0) {
    throw "Upload failed with exit code $LASTEXITCODE"
}

$upload = $uploadRaw | ConvertFrom-Json
Write-Host "Uploaded document_id: $($upload.document_id)"
Write-Host "Uploaded filename: $($upload.filename)"

$ocr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/ocr/mock"
Write-Host "OCR status: $($ocr.status)"

$ragBody = @{
    query = $Query
    top_k = $TopK
} | ConvertTo-Json
$rag = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/rag/query" -ContentType "application/json" -Body $ragBody

Write-Host ""
Write-Host "Answer:"
Write-Host $rag.answer

Write-Host ""
Write-Host "Citations:"
$rag.citations | ConvertTo-Json -Depth 8

Write-Host ""
Write-Host "Retrieved chunks:"
$rag.retrieved_chunks | ConvertTo-Json -Depth 8
