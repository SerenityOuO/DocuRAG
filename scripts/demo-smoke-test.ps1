param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = "",
    [switch]$RunRealOcr,
    [string]$RealOcrSamplePath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($SamplePath)) {
    $SamplePath = Join-Path $repoRoot "sample-data/documents/mock-invoice-aurora.txt"
}

if ([string]::IsNullOrWhiteSpace($RealOcrSamplePath)) {
    $RealOcrSamplePath = Join-Path $repoRoot "sample-data/documents/sample-ocr-invoice.png"
}

$resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path
$resolvedRealOcrSamplePath = (Resolve-Path -LiteralPath $RealOcrSamplePath).Path

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

if ($RunRealOcr) {
    Write-Host "Optional real OCR check"
    Write-Host "Real OCR sample: $resolvedRealOcrSamplePath"

    $realUploadRaw = & curl.exe -sS -X POST "$ApiBaseUrl/documents/upload" -F "file=@$resolvedRealOcrSamplePath;type=image/png"
    if ($LASTEXITCODE -ne 0) {
        throw "Real OCR sample upload failed with exit code $LASTEXITCODE"
    }

    $realUpload = $realUploadRaw | ConvertFrom-Json

    try {
        $realOcr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($realUpload.document_id)/ocr"
        Assert-Condition ($realOcr.status -eq "completed") "Provider-selected OCR did not complete."
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($realOcr.text)) "Provider-selected OCR returned empty text."
        Write-Host "Provider-selected OCR OK: $($realOcr.status)"

        $providerField = $null
        if ($realOcr.extracted_fields.PSObject.Properties.Name -contains "provider") {
            $providerField = $realOcr.extracted_fields.provider
        }

        if ($providerField -ne "paddleocr") {
            Write-Warning "Provider-selected OCR did not report provider=paddleocr. Check DOCURAG_OCR_PROVIDER if you expected real OCR."
        }
    }
    catch {
        Write-Warning "Optional real OCR check did not complete. Mock demo remains valid. $($_.Exception.Message)"
    }
}

Write-Host "Demo smoke test passed."
