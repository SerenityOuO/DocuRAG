param(
    [switch]$RunVector,
    [switch]$RunVectorRerank,
    [switch]$RunHybrid,
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$DatasetPath = "",
    [string]$SamplePath = "",
    [string]$OutputPath = "",
    [string]$EmbeddingBaseUrl = "http://127.0.0.1:11434",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
    [string]$RerankProvider = "fastembed",
    [string]$RerankModel = "BAAI/bge-reranker-base",
    [int]$RerankTopK = 5,
    [int]$RerankTimeoutSeconds = 30,
    [string]$QdrantUrl = "http://127.0.0.1:6333",
    [string]$QdrantCollection = "docurag_chunks_v1",
    [int]$QdrantVectorSize = 1024
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$venvPython = Join-Path $backendRoot ".venv/Scripts/python.exe"

if ([string]::IsNullOrWhiteSpace($DatasetPath)) {
    $DatasetPath = Join-Path $repoRoot "sample-data/eval/retrieval-eval.json"
}

if ([string]::IsNullOrWhiteSpace($SamplePath)) {
    $SamplePath = Join-Path $repoRoot "sample-data/documents/mock-invoice-aurora.txt"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $resultName = "retrieval-eval-result-keyword.json"
    if ($RunVector) {
        $resultName = "retrieval-eval-result-vector.json"
    }
    if ($RunVectorRerank) {
        $resultName = "retrieval-eval-result-vector-rerank.json"
    }
    if ($RunHybrid) {
        $resultName = "retrieval-eval-result-hybrid.json"
    }
    $OutputPath = Join-Path $repoRoot ".tmp/$resultName"
}

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

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment not found at $venvPython. Run scripts/test-backend.ps1 first."
}

$resolvedDatasetPath = (Resolve-Path -LiteralPath $DatasetPath).Path
$resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path
$strategy = "keyword"
$optionalModeCount = 0
if ($RunVector) { $optionalModeCount += 1 }
if ($RunVectorRerank) { $optionalModeCount += 1 }
if ($RunHybrid) { $optionalModeCount += 1 }
if ($optionalModeCount -gt 1) {
    throw "Use only one optional strategy flag: -RunVector, -RunVectorRerank, or -RunHybrid."
}

if ($RunVector -or $RunVectorRerank -or $RunHybrid) {
    if ($RunVectorRerank) {
        $strategy = "vector_rerank"
        $env:DOCURAG_RERANK_PROVIDER = $RerankProvider
        $env:DOCURAG_RERANK_MODEL = $RerankModel
        $env:DOCURAG_RERANK_TOP_K = [string]$RerankTopK
        $env:DOCURAG_RERANK_TIMEOUT_SECONDS = [string]$RerankTimeoutSeconds
    }
    elseif ($RunHybrid) {
        $strategy = "hybrid"
        $env:DOCURAG_RERANK_PROVIDER = ""
    }
    else {
        $strategy = "vector"
        $env:DOCURAG_RERANK_PROVIDER = ""
    }

    $env:DOCURAG_RAG_RETRIEVAL_PROVIDER = "vector"
    $env:DOCURAG_EMBEDDING_PROVIDER = "ollama"
    $env:DOCURAG_EMBEDDING_BASE_URL = $EmbeddingBaseUrl
    $env:DOCURAG_EMBEDDING_MODEL = $EmbeddingModel
    $env:DOCURAG_QDRANT_URL = $QdrantUrl
    $env:DOCURAG_QDRANT_COLLECTION = $QdrantCollection
    $env:DOCURAG_QDRANT_VECTOR_SIZE = [string]$QdrantVectorSize

    $embeddingTagsUrl = "$($EmbeddingBaseUrl.TrimEnd('/'))/api/tags"
    $qdrantCollectionUrl = "$($QdrantUrl.TrimEnd('/'))/collections/$QdrantCollection"

    Write-Host "Vector preflight"
    Write-Host "Ollama embedding tags: $embeddingTagsUrl"
    Write-Host "Qdrant collection: $qdrantCollectionUrl"
    Write-Host "Backend API: $ApiBaseUrl"
    if ($RunVectorRerank) {
        Write-Host "Rerank provider: $RerankProvider"
        Write-Host "Rerank model: $RerankModel"
    }

    try {
        $embeddingTags = Invoke-RestMethod -Method Get -Uri $embeddingTagsUrl
    }
    catch {
        throw "Ollama embedding service is required for optional vector-backed eval but $embeddingTagsUrl was unavailable. Start Ollama and pull $EmbeddingModel first. $($_.Exception.Message)"
    }

    $embeddingModelNames = @($embeddingTags.models | ForEach-Object { $_.name })
    Assert-Condition ($embeddingModelNames -contains $EmbeddingModel) "Ollama embedding model '$EmbeddingModel' was not found. Available models: $($embeddingModelNames -join ', ')"

    try {
        $qdrantCollectionInfo = Invoke-RestMethod -Method Get -Uri $qdrantCollectionUrl
    }
    catch {
        throw "Qdrant collection '$QdrantCollection' is required for optional vector-backed eval but $qdrantCollectionUrl was unavailable. Run scripts/qdrant-collection-smoke.ps1 first. $($_.Exception.Message)"
    }

    $vectors = $qdrantCollectionInfo.result.config.params.vectors
    Assert-Condition ([int]$vectors.size -eq $QdrantVectorSize) "Qdrant collection '$QdrantCollection' vector size is $($vectors.size); expected $QdrantVectorSize."
    Assert-Condition ([string]$vectors.distance -eq "Cosine") "Qdrant collection '$QdrantCollection' distance is $($vectors.distance); expected Cosine."

    try {
        $health = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/health"
    }
    catch {
        throw "Backend API is required for -RunVector manual indexing preflight but $ApiBaseUrl was unavailable. Start backend with vector env first. $($_.Exception.Message)"
    }

    Assert-Condition ($health.status -eq "ok") "Expected /health status ok."

    $upload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedSamplePath "text/plain"
    $ocr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/ocr/mock"
    Assert-Condition ($ocr.status -eq "completed") "OCR mock did not complete before vector indexing preflight."

    try {
        $vectorIndexing = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/index/vector"
    }
    catch {
        $errorBody = Get-ErrorResponseBody $_
        $detail = $_.Exception.Message
        if (-not [string]::IsNullOrWhiteSpace($errorBody)) {
            $detail = "$detail Response body: $errorBody"
        }

        throw "Manual vector indexing API preflight failed. Start backend with DOCURAG_EMBEDDING_PROVIDER=ollama, DOCURAG_EMBEDDING_MODEL=$EmbeddingModel, DOCURAG_QDRANT_URL=$QdrantUrl, and DOCURAG_QDRANT_COLLECTION=$QdrantCollection. $detail"
    }

    Assert-Condition ($vectorIndexing.status -eq "completed") "Expected manual vector indexing status completed. Got '$($vectorIndexing.status)'."
    Assert-Condition ($vectorIndexing.indexed_chunk_count -gt 0) "Manual vector indexing API did not index any chunks."
    Write-Host "Manual vector indexing API preflight OK: indexed chunks $($vectorIndexing.indexed_chunk_count)"
}
else {
    $env:DOCURAG_RAG_RETRIEVAL_PROVIDER = "keyword"
}

Write-Host "Retrieval eval smoke"
Write-Host "Strategy: $strategy"
Write-Host "Dataset: $resolvedDatasetPath"
Write-Host "Output: $OutputPath"

Push-Location $backendRoot
try {
    & $venvPython -m app.services.evaluation `
        --strategy $strategy `
        --dataset $resolvedDatasetPath `
        --sample-documents (Join-Path $repoRoot "sample-data/documents") `
        --output $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "Retrieval eval runner failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$result = Get-Content -Raw -LiteralPath $OutputPath | ConvertFrom-Json
Assert-Condition ($result.strategy -eq $strategy) "Expected strategy '$strategy'. Got '$($result.strategy)'."
Assert-Condition ($result.case_count -ge 4) "Expected at least 4 eval cases."
Assert-Condition ($result.results.Count -eq $result.case_count) "Result row count did not match case count."
Assert-Condition ($null -ne $result.summary.hit_rate_at_k) "Missing Hit Rate@K summary."
Assert-Condition ($null -ne $result.summary.mrr_at_k) "Missing MRR@K summary."
Assert-Condition ($null -ne $result.summary.recall_at_k) "Missing Recall@K summary."
Assert-Condition ($null -ne $result.summary.average_latency_ms) "Missing latency summary."
Assert-Condition ($null -ne $result.summary.failure_count) "Missing failure count summary."
Assert-Condition ($null -ne $result.summary.fallback_count) "Missing fallback count summary."
Assert-Condition ($null -ne $result.summary.trace_metadata_count) "Missing trace metadata count summary."
Assert-Condition ($null -ne $result.summary.result_strategy_counts) "Missing result strategy counts summary."
Assert-Condition ($null -ne $result.summary.fallback_reasons) "Missing fallback reasons summary."

if ($RunVector) {
    Assert-Condition ($result.summary.failure_count -eq 0) "Vector eval reported failures. Check Ollama embedding, Qdrant, and manual indexing readiness."
    Assert-Condition ($result.environment.retrieval_provider -eq "vector") "Vector eval did not report vector provider metadata."
    Assert-Condition ($result.environment.indexed_chunk_count -gt 0) "Vector eval did not index sample chunks."
}
elseif ($RunVectorRerank) {
    Assert-Condition ($result.environment.retrieval_provider -eq "vector_rerank") "Vector rerank eval did not report vector_rerank provider metadata."
    Assert-Condition ($result.environment.indexed_chunk_count -gt 0) "Vector rerank eval did not index sample chunks."
    Assert-Condition ($result.environment.rerank_provider -eq $RerankProvider) "Vector rerank eval did not report expected rerank provider metadata."

    $rerankMetadataRows = @($result.results | ForEach-Object { $_.retrieved_chunks } | Where-Object { $null -ne $_.metadata.rerank_enabled })
    Assert-Condition ($rerankMetadataRows.Count -gt 0) "Vector rerank eval did not include rerank trace metadata. Install optional rerank runtime or check fallback metadata."
}
elseif ($RunHybrid) {
    Assert-Condition ($result.summary.failure_count -eq 0) "Hybrid eval reported failures. Check Ollama embedding, Qdrant, and manual indexing readiness."
    Assert-Condition ($result.environment.retrieval_provider -eq "hybrid") "Hybrid eval did not report hybrid provider metadata."
    Assert-Condition ($result.environment.indexed_chunk_count -gt 0) "Hybrid eval did not index sample chunks."

    $hybridMetadataRows = @($result.results | ForEach-Object { $_.retrieved_chunks } | Where-Object { $_.metadata.strategy_label -eq "hybrid" })
    Assert-Condition ($hybridMetadataRows.Count -gt 0) "Hybrid eval did not include hybrid trace metadata."
}
else {
    Assert-Condition ($result.summary.failure_count -eq 0) "Keyword eval should not report failures."
    Assert-Condition ($result.summary.hit_rate_at_k -gt 0) "Keyword eval did not hit any expected evidence."
}

Write-Host "Retrieval eval smoke passed."
Write-Host "Hit Rate@K: $($result.summary.hit_rate_at_k)"
Write-Host "MRR@K: $($result.summary.mrr_at_k)"
Write-Host "Recall@K: $($result.summary.recall_at_k)"
Write-Host "Average latency ms: $($result.summary.average_latency_ms)"
Write-Host "Failure count: $($result.summary.failure_count)"
Write-Host "Fallback count: $($result.summary.fallback_count)"
Write-Host "Trace metadata count: $($result.summary.trace_metadata_count)"
Write-Host "Result strategy counts:"
$result.summary.result_strategy_counts | ConvertTo-Json -Depth 8
if ($result.summary.fallback_reasons.Count -gt 0) {
    Write-Host "Fallback reasons:"
    $result.summary.fallback_reasons | ConvertTo-Json -Depth 8
}
