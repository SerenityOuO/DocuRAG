param(
    [switch]$RunVector,
    [string]$DatasetPath = "",
    [string]$OutputPath = "",
    [string]$EmbeddingBaseUrl = "http://127.0.0.1:11434",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
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

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $resultName = "retrieval-eval-result-keyword.json"
    if ($RunVector) {
        $resultName = "retrieval-eval-result-vector.json"
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

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Backend virtual environment not found at $venvPython. Run scripts/test-backend.ps1 first."
}

$resolvedDatasetPath = (Resolve-Path -LiteralPath $DatasetPath).Path
$strategy = "keyword"
if ($RunVector) {
    $strategy = "vector"
    $env:DOCURAG_RAG_RETRIEVAL_PROVIDER = "vector"
    $env:DOCURAG_EMBEDDING_PROVIDER = "ollama"
    $env:DOCURAG_EMBEDDING_BASE_URL = $EmbeddingBaseUrl
    $env:DOCURAG_EMBEDDING_MODEL = $EmbeddingModel
    $env:DOCURAG_QDRANT_URL = $QdrantUrl
    $env:DOCURAG_QDRANT_COLLECTION = $QdrantCollection
    $env:DOCURAG_QDRANT_VECTOR_SIZE = [string]$QdrantVectorSize
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

if ($RunVector) {
    Assert-Condition ($result.summary.failure_count -eq 0) "Vector eval reported failures. Check Ollama embedding, Qdrant, and manual indexing readiness."
    Assert-Condition ($result.environment.retrieval_provider -eq "vector") "Vector eval did not report vector provider metadata."
    Assert-Condition ($result.environment.indexed_chunk_count -gt 0) "Vector eval did not index sample chunks."
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
