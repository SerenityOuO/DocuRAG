param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = "",
    [switch]$RunRealOcr,
    [string]$RealOcrSamplePath = "",
    [switch]$RunLlm,
    [string]$LlmBaseUrl = "http://127.0.0.1:11434",
    [string]$LlmModel = "qwen3.5:4b"
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

function Get-ErrorResponseBody {
    param([object]$ErrorRecord)

    $response = $ErrorRecord.Exception.Response
    if ($null -ne $ErrorRecord.ErrorDetails -and -not [string]::IsNullOrWhiteSpace($ErrorRecord.ErrorDetails.Message)) {
        return $ErrorRecord.ErrorDetails.Message
    }

    if ($null -eq $response) {
        return ""
    }

    try {
        $stream = $response.GetResponseStream()
        if ($null -eq $stream) {
            return ""
        }

        $reader = New-Object System.IO.StreamReader($stream)
        return $reader.ReadToEnd()
    }
    catch {
        return ""
    }
}

function Get-RagAnswerSource {
    param([object]$Rag)

    if ($null -eq $Rag -or $null -eq $Rag.citations -or $Rag.citations.Count -eq 0) {
        return "deterministic baseline"
    }

    $trace = $Rag.citations[0].trace_metadata
    if ($null -eq $trace) {
        return "deterministic baseline"
    }

    $statusProperty = $trace.PSObject.Properties["llm_generation_status"]
    if ($null -eq $statusProperty) {
        return "deterministic baseline"
    }

    if ($statusProperty.Value -eq "completed") {
        $provider = "ollama"
        $model = "qwen3.5:4b"
        $providerProperty = $trace.PSObject.Properties["llm_provider"]
        $modelProperty = $trace.PSObject.Properties["llm_model"]

        if ($null -ne $providerProperty -and -not [string]::IsNullOrWhiteSpace([string]$providerProperty.Value)) {
            $provider = [string]$providerProperty.Value
        }

        if ($null -ne $modelProperty -and -not [string]::IsNullOrWhiteSpace([string]$modelProperty.Value)) {
            $model = [string]$modelProperty.Value
        }

        return "$provider/$model"
    }

    if ($statusProperty.Value -eq "failed") {
        return "LLM unavailable fallback"
    }

    return "deterministic baseline"
}

function Invoke-FileUpload {
    param(
        [string]$Url,
        [string]$FilePath,
        [string]$ContentType
    )

    $tempBody = [System.IO.Path]::GetTempFileName()
    try {
        $httpStatus = & curl.exe -sS -o $tempBody -w "%{http_code}" -X POST $Url -F "file=@$FilePath;type=$ContentType"
        if ($LASTEXITCODE -ne 0) {
            throw "Upload failed with curl exit code $LASTEXITCODE"
        }

        $body = ""
        if (Test-Path -LiteralPath $tempBody) {
            $body = Get-Content -Raw -LiteralPath $tempBody
        }

        if ($httpStatus -notmatch "^2") {
            throw "Upload failed with HTTP $httpStatus. Response body: $body"
        }

        return $body | ConvertFrom-Json
    }
    finally {
        if (Test-Path -LiteralPath $tempBody) {
            Remove-Item -LiteralPath $tempBody -Force
        }
    }
}

Write-Host "Demo smoke test"
Write-Host "API: $ApiBaseUrl"

if ($RunLlm) {
    $ollamaTagsUrl = "$($LlmBaseUrl.TrimEnd('/'))/api/tags"
    Write-Host "LLM smoke enabled"
    Write-Host "Ollama tags: $ollamaTagsUrl"

    try {
        $ollamaTags = Invoke-RestMethod -Method Get -Uri $ollamaTagsUrl
    }
    catch {
        throw "Ollama is required for -RunLlm but $ollamaTagsUrl was unavailable. Start Ollama and pull $LlmModel first. $($_.Exception.Message)"
    }

    $modelNames = @($ollamaTags.models | ForEach-Object { $_.name })
    Assert-Condition ($modelNames -contains $LlmModel) "Ollama model '$LlmModel' was not found. Available models: $($modelNames -join ', ')"
}

$health = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/health"
Assert-Condition ($health.status -eq "ok") "Expected /health status ok."
Assert-Condition (-not [string]::IsNullOrWhiteSpace($health.version)) "Expected /health version."
Write-Host "Health OK: version $($health.version)"

$upload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedSamplePath "text/plain"
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

Assert-Condition ($rag.citations.Count -gt 0) "RAG did not return citations."
Assert-Condition ($rag.retrieved_chunks.Count -gt 0) "RAG did not return retrieved chunks."
Assert-Condition (($rag.retrieved_chunks | ConvertTo-Json -Depth 8) -match "AUR-2026-051") "Retrieved chunks did not include expected invoice evidence."
$ragAnswerSource = Get-RagAnswerSource $rag

if ($RunLlm) {
    $expectedSource = "ollama/$LlmModel"
    Assert-Condition ($ragAnswerSource -eq $expectedSource) "Expected LLM answer source '$expectedSource'. Got '$ragAnswerSource'. Start backend with DOCURAG_LLM_PROVIDER=ollama, DOCURAG_LLM_BASE_URL=$LlmBaseUrl, and DOCURAG_LLM_MODEL=$LlmModel."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($rag.answer)) "LLM RAG answer was empty."
    Assert-Condition ($rag.answer -notmatch "LLM generation unavailable") "LLM RAG fell back to deterministic answer."
}
else {
    Assert-Condition ($rag.answer -match "mock-invoice-aurora.txt") "RAG answer did not reference the sample invoice."
    Assert-Condition ($ragAnswerSource -eq "deterministic baseline") "Expected deterministic baseline answer source. Got '$ragAnswerSource'."
}

Write-Host "RAG query OK: source $ragAnswerSource"

if ($RunRealOcr) {
    Write-Host "Real OCR check"
    Write-Host "Real OCR sample: $resolvedRealOcrSamplePath"

    $realUpload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedRealOcrSamplePath "image/png"

    try {
        $realOcr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($realUpload.document_id)/ocr"
        Assert-Condition ($realOcr.status -eq "completed") "Provider-selected OCR did not complete."
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($realOcr.text)) "Provider-selected OCR returned empty text."
        Write-Host "Provider-selected OCR OK: $($realOcr.status)"

        $providerField = $null
        if ($realOcr.extracted_fields.PSObject.Properties.Name -contains "provider") {
            $providerField = $realOcr.extracted_fields.provider
        }

        Assert-Condition ($providerField -eq "paddleocr") "Provider-selected OCR did not report provider=paddleocr."

        $realDocument = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/documents/$($realUpload.document_id)"
        Assert-Condition ($realDocument.ocr.status -eq "completed") "Saved real OCR result did not complete."
        Assert-Condition ($realDocument.processing.ocr -eq "completed") "Real OCR processing status was not completed."
        Assert-Condition ($realDocument.processing.indexing -eq "completed") "Real OCR indexing status was not completed."
        Assert-Condition ($realDocument.processing.ready -eq $true) "Real OCR document was not marked ready."
        Assert-Condition ($realDocument.latest_job.status -eq "completed") "Latest real OCR job was not completed."
        Assert-Condition ($realDocument.chunks.Count -gt 0) "Real OCR did not create chunks."
        Write-Host "Provider-selected OCR metadata OK"
    }
    catch {
        $errorBody = Get-ErrorResponseBody $_
        $detail = $_.Exception.Message
        if (-not [string]::IsNullOrWhiteSpace($errorBody)) {
            $detail = "$detail Response body: $errorBody"
        }

        throw "Real OCR check did not complete. $detail"
    }
}

Write-Host "Demo smoke test passed."
