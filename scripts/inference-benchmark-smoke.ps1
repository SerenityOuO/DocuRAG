param(
    [string]$BaseUrl = "",
    [string]$Model = "",
    [string]$ApiKey = "",
    [int]$TimeoutSeconds = 10,
    [int]$MaxTokens = 32,
    [string]$Prompt = "Reply with exactly: DocuRAG inference benchmark OK.",
    [int]$ContextTokens = 4096,
    [int]$BatchSize = 1,
    [int]$HiddenSize = 4096,
    [int]$LayerCount = 32,
    [int]$DtypeBytes = 2,
    [double]$ModelParameterBillions = 7.0,
    [string]$OutputPath = "",
    [switch]$FailOnUnavailable
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PropertyValue {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = $env:DOCURAG_LLM_BASE_URL
}
if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
    $BaseUrl = "http://127.0.0.1:8000/v1"
}

if ([string]::IsNullOrWhiteSpace($Model)) {
    $Model = $env:DOCURAG_LLM_MODEL
}
if ([string]::IsNullOrWhiteSpace($Model)) {
    $Model = "Qwen/Qwen3-0.6B"
}

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    $ApiKey = $env:DOCURAG_LLM_API_KEY
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repoRoot ".tmp/inference-benchmark-smoke.json"
}
elseif (-not [System.IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $repoRoot $OutputPath
}

$outputDirectory = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$baseUrlTrimmed = $BaseUrl.TrimEnd("/")
$completionUrl = "$baseUrlTrimmed/chat/completions"
$kvCacheEstimateMb = [math]::Round(($LayerCount * 2.0 * $ContextTokens * $HiddenSize * $DtypeBytes * $BatchSize) / 1MB, 2)
$modelMemoryEstimateMb = [math]::Round(($ModelParameterBillions * 1000000000.0 * $DtypeBytes) / 1MB, 2)
$gpuMemoryEstimateMb = [math]::Round($kvCacheEstimateMb + $modelMemoryEstimateMb, 2)
$timestamp = (Get-Date).ToUniversalTime().ToString("o")

$estimateBlock = [ordered]@{
    estimate_only = $true
    kv_cache_estimate_mb = $kvCacheEstimateMb
    model_memory_estimate_mb = $modelMemoryEstimateMb
    gpu_memory_estimate_mb = $gpuMemoryEstimateMb
    context_tokens = $ContextTokens
    batch_size = $BatchSize
    hidden_size = $HiddenSize
    layer_count = $LayerCount
    dtype_bytes = $DtypeBytes
    model_parameter_billions = $ModelParameterBillions
}

Write-Host "Inference benchmark smoke"
Write-Host "Endpoint: $completionUrl"
Write-Host "Model: $Model"
Write-Host "Output: $OutputPath"

$body = @{
    model = $Model
    messages = @(
        @{
            role = "user"
            content = $Prompt
        }
    )
    stream = $false
    max_tokens = $MaxTokens
} | ConvertTo-Json -Depth 6

$headers = @{}
if (-not [string]::IsNullOrWhiteSpace($ApiKey)) {
    $headers["Authorization"] = "Bearer $ApiKey"
}

$malformedResponse = $false

try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri $completionUrl `
        -ContentType "application/json" `
        -Headers $headers `
        -Body $body `
        -TimeoutSec $TimeoutSeconds
    $stopwatch.Stop()

    $latencyMs = [math]::Round($stopwatch.Elapsed.TotalMilliseconds, 2)
    $usage = Get-PropertyValue $response "usage"
    $choicesValue = Get-PropertyValue $response "choices"
    $choices = if ($null -eq $choicesValue) { @() } else { @($choicesValue) }
    $firstChoice = if ($choices.Count -gt 0) { $choices[0] } else { $null }
    $message = Get-PropertyValue $firstChoice "message"
    $content = Get-PropertyValue $message "content"
    $completionTokens = Get-PropertyValue $usage "completion_tokens"
    $promptTokens = Get-PropertyValue $usage "prompt_tokens"
    $totalTokens = Get-PropertyValue $usage "total_tokens"
    $finishReason = Get-PropertyValue $firstChoice "finish_reason"
    $providerRequestId = Get-PropertyValue $response "id"

    if ([string]::IsNullOrWhiteSpace($content)) {
        $malformedResponse = $true
        $failedReport = [ordered]@{
            status = "failed"
            provider = "vllm_openai_compatible"
            provider_status = "malformed_response"
            generated_at = $timestamp
            endpoint = $completionUrl
            model = $Model
            max_tokens = $MaxTokens
            timeout_seconds = $TimeoutSeconds
            metrics = [ordered]@{
                latency_ms = $latencyMs
                prompt_tokens = $promptTokens
                completion_tokens = $completionTokens
                total_tokens = $totalTokens
                throughput_tokens_per_second = $null
                finish_reason = $finishReason
                provider_request_id = $providerRequestId
            }
            estimates = $estimateBlock
            fallback = [ordered]@{
                fallback_target = "ollama_or_deterministic"
                fallback_reason = "malformed_response"
            }
        }
        $failedReport | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8
        throw "OpenAI-compatible response did not contain choices[0].message.content."
    }

    $throughputTokensPerSecond = $null
    if ($null -ne $completionTokens -and $latencyMs -gt 0) {
        $throughputTokensPerSecond = [math]::Round(([double]$completionTokens) / ($latencyMs / 1000.0), 2)
    }

    $completedReport = [ordered]@{
        status = "completed"
        provider = "vllm_openai_compatible"
        provider_status = "available"
        generated_at = $timestamp
        endpoint = $completionUrl
        model = $Model
        max_tokens = $MaxTokens
        timeout_seconds = $TimeoutSeconds
        metrics = [ordered]@{
            latency_ms = $latencyMs
            prompt_tokens = $promptTokens
            completion_tokens = $completionTokens
            total_tokens = $totalTokens
            throughput_tokens_per_second = $throughputTokensPerSecond
            finish_reason = $finishReason
            provider_request_id = $providerRequestId
        }
        estimates = $estimateBlock
        fallback = [ordered]@{
            fallback_target = "none"
            fallback_reason = $null
        }
        response_preview = $content
    }

    $completedReport | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8

    Write-Host "Benchmark completed."
    Write-Host "Latency ms: $latencyMs"
    Write-Host "Prompt tokens: $promptTokens"
    Write-Host "Completion tokens: $completionTokens"
    Write-Host "Throughput tokens/sec: $throughputTokensPerSecond"
    Write-Host "KV cache estimate MB: $kvCacheEstimateMb"
    Write-Host "GPU memory estimate MB: $gpuMemoryEstimateMb"
}
catch {
    if ($malformedResponse) {
        throw
    }

    $skipReason = $_.Exception.Message
    $skippedReport = [ordered]@{
        status = "skipped"
        provider = "vllm_openai_compatible"
        provider_status = "unavailable"
        generated_at = $timestamp
        endpoint = $completionUrl
        model = $Model
        max_tokens = $MaxTokens
        timeout_seconds = $TimeoutSeconds
        skip_reason = $skipReason
        metrics = [ordered]@{
            latency_ms = $null
            prompt_tokens = $null
            completion_tokens = $null
            total_tokens = $null
            throughput_tokens_per_second = $null
            finish_reason = $null
            provider_request_id = $null
        }
        estimates = $estimateBlock
        fallback = [ordered]@{
            fallback_target = "ollama_or_deterministic"
            fallback_reason = "provider_unavailable"
            operator_action = "Use DOCURAG_LLM_PROVIDER=ollama for local fallback, or set DOCURAG_LLM_PROVIDER= to keep deterministic baseline."
        }
    }

    $skippedReport | ConvertTo-Json -Depth 8 | Set-Content -Path $OutputPath -Encoding UTF8

    Write-Host "vLLM OpenAI-compatible endpoint unavailable; benchmark skipped."
    Write-Host "Reason: $skipReason"
    Write-Host "Fallback: use DOCURAG_LLM_PROVIDER=ollama or set DOCURAG_LLM_PROVIDER= for deterministic baseline."
    Write-Host "Report: $OutputPath"

    if ($FailOnUnavailable) {
        throw
    }
}
