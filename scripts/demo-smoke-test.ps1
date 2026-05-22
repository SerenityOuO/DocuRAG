param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = "",
    [switch]$RunRealOcr,
    [string]$RealOcrSamplePath = "",
    [switch]$RunLlm,
    [string]$LlmBaseUrl = "http://127.0.0.1:11434",
    [string]$LlmModel = "qwen3.5:4b",
    [switch]$RunVector,
    [string]$EmbeddingBaseUrl = "http://127.0.0.1:11434",
    [string]$EmbeddingModel = "qwen3-embedding:0.6b",
    [string]$QdrantUrl = "http://127.0.0.1:6333",
    [string]$QdrantCollection = "docurag_chunks_v1",
    [int]$QdrantVectorSize = 1024
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

function Get-RagRetrievalSource {
    param([object]$Rag)

    $trace = $null
    if ($null -ne $Rag -and $null -ne $Rag.citations -and $Rag.citations.Count -gt 0) {
        $trace = $Rag.citations[0].trace_metadata
    }
    elseif ($null -ne $Rag -and $null -ne $Rag.retrieved_chunks -and $Rag.retrieved_chunks.Count -gt 0) {
        $trace = $Rag.retrieved_chunks[0].metadata
    }

    if ($null -eq $trace) {
        return "keyword baseline"
    }

    $statusProperty = $trace.PSObject.Properties["vector_retrieval_status"]
    if ($null -eq $statusProperty) {
        return "keyword baseline"
    }

    if ($statusProperty.Value -eq "completed") {
        $provider = "vector"
        $store = "qdrant"
        $providerProperty = $trace.PSObject.Properties["retrieval_provider"]
        $storeProperty = $trace.PSObject.Properties["vector_store"]

        if ($null -ne $providerProperty -and -not [string]::IsNullOrWhiteSpace([string]$providerProperty.Value)) {
            $provider = [string]$providerProperty.Value
        }

        if ($null -ne $storeProperty -and -not [string]::IsNullOrWhiteSpace([string]$storeProperty.Value)) {
            $store = [string]$storeProperty.Value
        }

        return "$provider/$store"
    }

    if ($statusProperty.Value -eq "failed") {
        return "vector unavailable fallback"
    }

    return "keyword baseline"
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

if ($RunVector) {
    $embeddingTagsUrl = "$($EmbeddingBaseUrl.TrimEnd('/'))/api/tags"
    $qdrantCollectionsUrl = "$($QdrantUrl.TrimEnd('/'))/collections"
    $qdrantCollectionUrl = "$($QdrantUrl.TrimEnd('/'))/collections/$QdrantCollection"
    Write-Host "Vector smoke enabled"
    Write-Host "Ollama embedding tags: $embeddingTagsUrl"
    Write-Host "Qdrant collections: $qdrantCollectionsUrl"
    Write-Host "Qdrant collection: $qdrantCollectionUrl"

    try {
        $embeddingTags = Invoke-RestMethod -Method Get -Uri $embeddingTagsUrl
    }
    catch {
        throw "Ollama embedding service is required for -RunVector but $embeddingTagsUrl was unavailable. Start Ollama and pull $EmbeddingModel first. $($_.Exception.Message)"
    }

    $embeddingModelNames = @($embeddingTags.models | ForEach-Object { $_.name })
    Assert-Condition ($embeddingModelNames -contains $EmbeddingModel) "Ollama embedding model '$EmbeddingModel' was not found. Available models: $($embeddingModelNames -join ', ')"

    try {
        Invoke-RestMethod -Method Get -Uri $qdrantCollectionsUrl | Out-Null
    }
    catch {
        throw "Qdrant is required for -RunVector but $qdrantCollectionsUrl was unavailable. Start docker-compose Qdrant first. $($_.Exception.Message)"
    }

    try {
        $qdrantCollectionInfo = Invoke-RestMethod -Method Get -Uri $qdrantCollectionUrl
    }
    catch {
        throw "Qdrant collection '$QdrantCollection' is required for -RunVector but $qdrantCollectionUrl was unavailable. Run scripts/qdrant-collection-smoke.ps1 first. $($_.Exception.Message)"
    }

    $vectors = $qdrantCollectionInfo.result.config.params.vectors
    Assert-Condition ([int]$vectors.size -eq $QdrantVectorSize) "Qdrant collection '$QdrantCollection' vector size is $($vectors.size); expected $QdrantVectorSize."
    Assert-Condition ([string]$vectors.distance -eq "Cosine") "Qdrant collection '$QdrantCollection' distance is $($vectors.distance); expected Cosine."
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

if ($RunVector) {
    Write-Host "Manual vector indexing"

    try {
        $vectorIndexing = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/index/vector"
    }
    catch {
        $errorBody = Get-ErrorResponseBody $_
        $detail = $_.Exception.Message
        if (-not [string]::IsNullOrWhiteSpace($errorBody)) {
            $detail = "$detail Response body: $errorBody"
        }

        throw "Manual vector indexing failed. Start backend with DOCURAG_EMBEDDING_PROVIDER=ollama, DOCURAG_EMBEDDING_MODEL=$EmbeddingModel, DOCURAG_QDRANT_URL=$QdrantUrl, and DOCURAG_QDRANT_COLLECTION=$QdrantCollection. $detail"
    }

    Assert-Condition ($vectorIndexing.status -eq "completed") "Expected manual vector indexing status completed. Got '$($vectorIndexing.status)'."
    Assert-Condition ($vectorIndexing.indexed_chunk_count -gt 0) "Manual vector indexing did not index any chunks."
    Assert-Condition ($vectorIndexing.collection_name -eq $QdrantCollection) "Manual vector indexing used unexpected collection '$($vectorIndexing.collection_name)'."
    Assert-Condition ($vectorIndexing.vector_size -eq $QdrantVectorSize) "Manual vector indexing used vector size $($vectorIndexing.vector_size); expected $QdrantVectorSize."
    Assert-Condition ($vectorIndexing.embedding_model -eq $EmbeddingModel) "Manual vector indexing used embedding model '$($vectorIndexing.embedding_model)'; expected '$EmbeddingModel'."
    Write-Host "Manual vector indexing OK: indexed chunks $($vectorIndexing.indexed_chunk_count)"
}

$ragBody = @{
    query = "payment due date Net 15"
    top_k = 3
} | ConvertTo-Json
$rag = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/rag/query" -ContentType "application/json" -Body $ragBody

Assert-Condition ($rag.citations.Count -gt 0) "RAG did not return citations."
Assert-Condition ($rag.retrieved_chunks.Count -gt 0) "RAG did not return retrieved chunks."
Assert-Condition (($rag.retrieved_chunks | ConvertTo-Json -Depth 8) -match "AUR-2026-051") "Retrieved chunks did not include expected invoice evidence."
$ragAnswerSource = Get-RagAnswerSource $rag
$ragRetrievalSource = Get-RagRetrievalSource $rag

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

if ($RunVector) {
    Assert-Condition ($ragRetrievalSource -eq "vector/qdrant") "Expected vector retrieval source 'vector/qdrant'. Got '$ragRetrievalSource'. Start backend with DOCURAG_RAG_RETRIEVAL_PROVIDER=vector, DOCURAG_EMBEDDING_PROVIDER=ollama, DOCURAG_EMBEDDING_MODEL=$EmbeddingModel, DOCURAG_QDRANT_URL=$QdrantUrl, and DOCURAG_QDRANT_COLLECTION=$QdrantCollection."
}
else {
    Assert-Condition ($ragRetrievalSource -eq "keyword baseline") "Expected keyword baseline retrieval source. Got '$ragRetrievalSource'."
}

Write-Host "RAG query OK: answer source $ragAnswerSource; retrieval source $ragRetrievalSource"

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
