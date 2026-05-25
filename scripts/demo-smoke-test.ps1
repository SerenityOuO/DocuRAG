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
    [int]$QdrantVectorSize = 1024,
    [string]$ExpectedVersion = "0.28.0",
    [switch]$RunVlmFake
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

    $strategyProperty = $trace.PSObject.Properties["strategy_label"]
    if ($null -ne $strategyProperty -and -not [string]::IsNullOrWhiteSpace([string]$strategyProperty.Value)) {
        $strategy = [string]$strategyProperty.Value
        $fallbackState = $trace.PSObject.Properties["fallback_state"]
        $rerankStatus = $trace.PSObject.Properties["rerank_status"]

        if ($null -ne $fallbackState -and -not [string]::IsNullOrWhiteSpace([string]$fallbackState.Value) -and [string]$fallbackState.Value -ne "none") {
            return "$strategy fallback: $($fallbackState.Value)"
        }

        if ($null -ne $rerankStatus -and -not [string]::IsNullOrWhiteSpace([string]$rerankStatus.Value) -and [string]$rerankStatus.Value -ne "completed") {
            return "$strategy fallback: rerank_$($rerankStatus.Value)"
        }

        return $strategy
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
        [string]$ContentType,
        [hashtable]$Headers = @{}
    )

    $tempBody = [System.IO.Path]::GetTempFileName()
    try {
        $curlArgs = @("-sS", "-o", $tempBody, "-w", "%{http_code}", "-X", "POST", $Url)
        foreach ($header in $Headers.GetEnumerator()) {
            $curlArgs += @("-H", "$($header.Key): $($header.Value)")
        }
        $curlArgs += @("-F", "file=@$FilePath;type=$ContentType")

        $httpStatus = & curl.exe @curlArgs
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
Assert-Condition ($health.version -eq $ExpectedVersion) "Expected /health version $ExpectedVersion. Got $($health.version). Restart the backend after release sync."
Write-Host "Health OK: version $($health.version)"

$authHeaders = @{}
$authState = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/auth/me"
if ($authState.auth_mode -eq "demo" -and $authState.authenticated -ne $true) {
    $loginBody = @{
        username = "admin"
        password = "demo-admin-pass"
    } | ConvertTo-Json
    $login = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/auth/login" -ContentType "application/json" -Body $loginBody
    Assert-Condition ($login.user.role -eq "admin") "Demo auth login did not return admin role."
    $authHeaders = @{
        Authorization = "Bearer $($login.access_token)"
    }
    Write-Host "Demo auth OK: admin login"
}
elseif ($authState.auth_mode -eq "demo") {
    Write-Host "Demo auth OK: existing session"
}
else {
    Write-Host "Demo auth disabled"
}

$upload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedSamplePath "text/plain" $authHeaders
Assert-Condition (-not [string]::IsNullOrWhiteSpace($upload.document_id)) "Upload did not return document_id."
Assert-Condition ($upload.filename -eq "mock-invoice-aurora.txt") "Upload returned unexpected filename."
Assert-Condition ($upload.ocr.status -eq "pending") "Direct text upload should not mark OCR completed."
Assert-Condition ($upload.processing.ocr -eq "pending") "Direct text upload processing should keep OCR pending."
Assert-Condition ($upload.processing.indexing -eq "completed") "Direct text upload did not complete local indexing."
Assert-Condition ($upload.chunks.Count -gt 0) "Direct text upload did not create chunks."
Assert-Condition ($upload.chunks[0].source_type -eq "text_upload") "Direct text upload chunk source_type was '$($upload.chunks[0].source_type)'; expected text_upload."
Assert-Condition ($upload.chunks[0].metadata.origin -eq "uploaded_text") "Direct text upload chunk origin was '$($upload.chunks[0].metadata.origin)'; expected uploaded_text."
Write-Host "Upload OK: $($upload.document_id)"
Write-Host "Direct text ingestion OK"

$parser = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/parse" -Headers $authHeaders
Assert-Condition ($parser.status -eq "parsed") "Parser did not return parsed status."
Assert-Condition ($parser.parser_source -eq "deterministic_invoice") "Parser source was '$($parser.parser_source)'; expected deterministic_invoice."
Assert-Condition ($parser.fallback_reason -eq "unsupported_file") "Parser fallback reason was '$($parser.fallback_reason)'; expected unsupported_file."
Assert-Condition ($parser.trace_metadata.fallback_chain -eq "vlm_invoice -> deterministic_invoice") "Parser fallback chain was '$($parser.trace_metadata.fallback_chain)'; expected vlm_invoice -> deterministic_invoice."
Assert-Condition ($parser.trace_metadata.fallback_reason -eq "unsupported_file") "Parser trace fallback reason was '$($parser.trace_metadata.fallback_reason)'; expected unsupported_file."
Assert-Condition ($parser.fields.invoice_number.value -eq "AUR-2026-051") "Parser did not extract invoice number AUR-2026-051."
Assert-Condition ($parser.fields.vendor_name.value -eq "Aurora Office Supplies Demo LLC") "Parser did not extract expected vendor."
Assert-Condition ([double]$parser.fields.total_amount.value -eq 1248.5) "Parser did not extract expected total amount."
Assert-Condition ($parser.fields.currency.value -eq "USD") "Parser did not extract expected currency."
Assert-Condition (-not [string]::IsNullOrWhiteSpace([string]$parser.fields.invoice_number.source_text)) "Parser did not preserve invoice number source text."

$fields = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/documents/$($upload.document_id)/fields"
Assert-Condition ($fields.status -eq "parsed") "Saved fields lookup did not return parsed status."
Assert-Condition ($fields.fields.invoice_number.value -eq "AUR-2026-051") "Saved fields lookup did not return invoice number AUR-2026-051."
Assert-Condition ($fields.fields.total_amount.value -eq $parser.fields.total_amount.value) "Saved fields lookup total amount did not match parser result."
Write-Host "Parser fields OK: invoice $($fields.fields.invoice_number.value); total $($fields.fields.total_amount.value) $($fields.fields.currency.value)"

$agentBody = @{
    task = "Summarize invoice fields and cite payment terms."
    document_id = $upload.document_id
    query = "payment terms"
    top_k = 3
} | ConvertTo-Json
$agentRun = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/agent/run" -ContentType "application/json" -Body $agentBody

Assert-Condition (-not [string]::IsNullOrWhiteSpace($agentRun.run_id)) "Agent run did not return run_id."
Assert-Condition ($agentRun.status -eq "completed") "Agent run did not complete. Got '$($agentRun.status)'."
Assert-Condition ($agentRun.trace.planner -eq "deterministic") "Agent planner trace was '$($agentRun.trace.planner)'; expected deterministic."
Assert-Condition ($agentRun.trace.tool_policy -eq "allowlisted_read_only") "Agent tool policy was '$($agentRun.trace.tool_policy)'; expected allowlisted_read_only."
Assert-Condition ($agentRun.plan_steps.Count -eq 3) "Agent run expected 3 plan steps. Got $($agentRun.plan_steps.Count)."
Assert-Condition ($agentRun.tool_calls.Count -eq 3) "Agent run expected 3 tool calls. Got $($agentRun.tool_calls.Count)."
$agentToolNames = @($agentRun.tool_calls | ForEach-Object { $_.tool_name })
Assert-Condition ($agentToolNames[0] -eq "get_document_fields") "Agent first tool was '$($agentToolNames[0])'; expected get_document_fields."
Assert-Condition ($agentToolNames[1] -eq "search_documents") "Agent second tool was '$($agentToolNames[1])'; expected search_documents."
Assert-Condition ($agentToolNames[2] -eq "summarize_invoice_fields") "Agent third tool was '$($agentToolNames[2])'; expected summarize_invoice_fields."
Assert-Condition ($agentRun.final_answer.status -eq "completed") "Agent final answer did not complete."
Assert-Condition ($agentRun.final_answer.text -match "Invoice AUR-2026-051") "Agent final answer did not include expected invoice summary."
Assert-Condition ($agentRun.citations.Count -gt 0) "Agent run did not return citations."
Assert-Condition ($agentRun.citations[0].source_type -eq "text_upload") "Agent citation source_type was '$($agentRun.citations[0].source_type)'; expected text_upload."
Assert-Condition ($agentRun.tool_calls[0].observation.fallback_reason -eq "unsupported_file") "Agent get_document_fields did not expose parser fallback reason unsupported_file."
Assert-Condition ($agentRun.tool_calls[0].output.parser_source -eq "deterministic_invoice") "Agent get_document_fields did not expose deterministic parser source."

$agentLookup = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/agent/runs/$($agentRun.run_id)"
Assert-Condition ($agentLookup.run_id -eq $agentRun.run_id) "Agent lookup did not return the saved run."
Assert-Condition ($agentLookup.status -eq $agentRun.status) "Agent lookup status did not match original run."
Write-Host "Agent run OK: $($agentRun.run_id); tools $($agentToolNames -join ' -> ')"

$vlmFakeEnabled = $RunVlmFake -or ([string]$env:DOCURAG_VLM_PROVIDER).Trim().ToLowerInvariant() -eq "fake"
if ($vlmFakeEnabled) {
    Write-Host "VLM fake provider success check"

    $vlmUpload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedRealOcrSamplePath "image/png" $authHeaders
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($vlmUpload.document_id)) "VLM fake upload did not return document_id."

    $vlmOcr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($vlmUpload.document_id)/ocr/mock" -Headers $authHeaders
    Assert-Condition ($vlmOcr.status -eq "completed") "VLM fake OCR mock did not complete."

    $vlmParser = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($vlmUpload.document_id)/parse" -Headers $authHeaders
    Assert-Condition ($vlmParser.status -eq "parsed") "VLM fake parser did not return parsed status."
    Assert-Condition ($vlmParser.parser_source -eq "vlm_invoice") "VLM fake parser source was '$($vlmParser.parser_source)'; expected vlm_invoice."
    Assert-Condition ($null -eq $vlmParser.fallback_reason) "VLM fake parser fallback reason should be null. Got '$($vlmParser.fallback_reason)'."
    Assert-Condition ($vlmParser.trace_metadata.vlm_provider -eq "fake") "VLM fake parser did not report vlm_provider=fake."
    Assert-Condition ($vlmParser.trace_metadata.fallback_chain -eq "vlm_invoice") "VLM fake parser fallback chain was '$($vlmParser.trace_metadata.fallback_chain)'; expected vlm_invoice."
    Assert-Condition ($vlmParser.trace_metadata.ocr_context_state -eq "available") "VLM fake parser did not receive OCR context."
    Assert-Condition ([int]$vlmParser.trace_metadata.ocr_context_line_count -gt 0) "VLM fake parser OCR context line count was not positive."
    Assert-Condition ($vlmParser.fields.invoice_number.value -eq "AUR-2026-051") "VLM fake parser did not extract invoice AUR-2026-051."
    Assert-Condition ($vlmParser.fields.invoice_number.parser_source -eq "vlm_invoice") "VLM fake parser did not preserve field parser_source=vlm_invoice."
    Assert-Condition ($vlmParser.fields.invoice_number.fallback_reason -eq "evidence_unmatched") "VLM fake parser should mark invoice number OCR evidence as unmatched for the mock image OCR path."

    $vlmAgentBody = @{
        task = "Summarize invoice fields from the VLM parser result."
        document_id = $vlmUpload.document_id
        query = "Mock OCR result sample-ocr-invoice"
        top_k = 3
    } | ConvertTo-Json
    $vlmAgentRun = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/agent/run" -ContentType "application/json" -Body $vlmAgentBody

    Assert-Condition ($vlmAgentRun.status -eq "completed") "VLM fake Agent run did not complete. Got '$($vlmAgentRun.status)'."
    Assert-Condition ($vlmAgentRun.tool_calls[0].tool_name -eq "get_document_fields") "VLM fake Agent first tool was '$($vlmAgentRun.tool_calls[0].tool_name)'; expected get_document_fields."
    Assert-Condition ($vlmAgentRun.tool_calls[0].output.parser_source -eq "vlm_invoice") "VLM fake Agent get_document_fields did not expose parser_source=vlm_invoice."
    Assert-Condition ($null -eq $vlmAgentRun.tool_calls[0].observation.fallback_reason) "VLM fake Agent get_document_fields should not expose fallback reason."
    Assert-Condition ($vlmAgentRun.final_answer.text -match "Invoice AUR-2026-051") "VLM fake Agent final answer did not include invoice summary."
    Write-Host "VLM fake parser OK: parser source $($vlmParser.parser_source); Agent $($vlmAgentRun.run_id)"
}
else {
    Write-Host "VLM fake provider success check skipped; set DOCURAG_VLM_PROVIDER=fake or pass -RunVlmFake."
}

if ($RunVector) {
    Write-Host "Manual vector indexing"

    try {
        $vectorIndexing = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/index/vector" -Headers $authHeaders
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
else {
    Write-Host "Aggressive default vector indexing best-effort"

    try {
        $defaultVectorIndexing = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/index/vector" -Headers $authHeaders
        if ($defaultVectorIndexing.status -eq "completed") {
            Write-Host "Aggressive vector indexing OK: indexed chunks $($defaultVectorIndexing.indexed_chunk_count)"
        }
        else {
            Write-Host "Aggressive vector indexing skipped: status $($defaultVectorIndexing.status)"
        }
    }
    catch {
        $errorBody = Get-ErrorResponseBody $_
        $detail = $_.Exception.Message
        if (-not [string]::IsNullOrWhiteSpace($errorBody)) {
            $detail = "$detail Response body: $errorBody"
        }

        Write-Host "Aggressive vector indexing unavailable; RAG fallback is expected in local baseline. $detail"
    }
}

$ragBody = @{
    query = "payment due date Net 15"
    top_k = 3
} | ConvertTo-Json
$rag = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/rag/query" -ContentType "application/json" -Body $ragBody

Assert-Condition ($rag.citations.Count -gt 0) "RAG did not return citations."
Assert-Condition ($rag.retrieved_chunks.Count -gt 0) "RAG did not return retrieved chunks."
Assert-Condition (($rag.retrieved_chunks | ConvertTo-Json -Depth 8) -match "AUR-2026-051") "Retrieved chunks did not include expected invoice evidence."
Assert-Condition ($rag.citations[0].source_type -eq "text_upload") "RAG citation source_type was '$($rag.citations[0].source_type)'; expected text_upload."
$ragAnswerSource = Get-RagAnswerSource $rag
$ragRetrievalSource = Get-RagRetrievalSource $rag

if ($RunLlm) {
    $expectedSource = "ollama/$LlmModel"
    Assert-Condition ($ragAnswerSource -eq $expectedSource) "Expected LLM answer source '$expectedSource'. Got '$ragAnswerSource'. Start backend with DOCURAG_LLM_PROVIDER=ollama, DOCURAG_LLM_BASE_URL=$LlmBaseUrl, and DOCURAG_LLM_MODEL=$LlmModel."
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($rag.answer)) "LLM RAG answer was empty."
    Assert-Condition ($rag.answer -notmatch "LLM generation unavailable") "LLM RAG fell back to deterministic answer."
}
else {
    $acceptedDefaultSources = @("deterministic baseline", "LLM unavailable fallback", "ollama/$LlmModel")
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($rag.answer)) "Default RAG answer was empty."
    Assert-Condition ($acceptedDefaultSources -contains $ragAnswerSource) "Expected default answer source to be deterministic baseline, LLM unavailable fallback, or ollama/$LlmModel. Got '$ragAnswerSource'."
}

if ($RunVector) {
    $acceptedVectorSources = @("vector/qdrant", "vector_rerank", "hybrid", "hybrid_rerank")
    $hasAcceptedVectorSource = $false
    foreach ($source in $acceptedVectorSources) {
        if ($ragRetrievalSource.StartsWith($source)) {
            $hasAcceptedVectorSource = $true
        }
    }

    Assert-Condition $hasAcceptedVectorSource "Expected vector-backed retrieval source. Got '$ragRetrievalSource'. Start backend with DOCURAG_RAG_RETRIEVAL_PROVIDER=vector or hybrid_rerank, DOCURAG_EMBEDDING_PROVIDER=ollama, DOCURAG_EMBEDDING_MODEL=$EmbeddingModel, DOCURAG_QDRANT_URL=$QdrantUrl, and DOCURAG_QDRANT_COLLECTION=$QdrantCollection."
}
else {
    $acceptedDefaultSources = @("keyword baseline", "vector unavailable fallback", "vector/qdrant", "vector_rerank", "hybrid", "hybrid_rerank")
    $hasAcceptedDefaultSource = $false
    foreach ($source in $acceptedDefaultSources) {
        if ($ragRetrievalSource.StartsWith($source)) {
            $hasAcceptedDefaultSource = $true
        }
    }

    Assert-Condition $hasAcceptedDefaultSource "Expected aggressive default retrieval source or fallback. Got '$ragRetrievalSource'."
}

Write-Host "RAG query OK: answer source $ragAnswerSource; retrieval source $ragRetrievalSource"

if ($RunRealOcr) {
    Write-Host "Real OCR check"
    Write-Host "Real OCR sample: $resolvedRealOcrSamplePath"

    $realUpload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedRealOcrSamplePath "image/png" $authHeaders

    try {
        $realOcr = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($realUpload.document_id)/ocr" -Headers $authHeaders
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
