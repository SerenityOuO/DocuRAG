param(
    [string]$DatasetPath = "",
    [string]$MetadataPath = "",
    [string]$BaselinePath = "",
    [string]$CurrentResultPath = "",
    [string]$OutputPath = "",
    [string]$Strategy = "keyword"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$evalSmokeScript = Join-Path $PSScriptRoot "retrieval-eval-smoke.ps1"

if ([string]::IsNullOrWhiteSpace($DatasetPath)) {
    $DatasetPath = Join-Path $repoRoot "sample-data/eval/retrieval-eval.json"
}

if ([string]::IsNullOrWhiteSpace($MetadataPath)) {
    $MetadataPath = Join-Path $repoRoot "sample-data/eval/golden-dataset-metadata.json"
}

if ([string]::IsNullOrWhiteSpace($BaselinePath)) {
    $BaselinePath = Join-Path $repoRoot "sample-data/eval/retrieval-regression-baseline.json"
}

if ([string]::IsNullOrWhiteSpace($CurrentResultPath)) {
    $CurrentResultPath = Join-Path $repoRoot ".tmp/retrieval-regression-current-keyword.json"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = Join-Path $repoRoot ".tmp/retrieval-regression-report.json"
}

function Read-JsonFile {
    param([string]$Path)

    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    $text = [System.IO.File]::ReadAllText($resolvedPath, [System.Text.Encoding]::UTF8)
    return $text | ConvertFrom-Json
}

function Write-JsonFile {
    param(
        [string]$Path,
        [object]$Value
    )

    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $json = $Value | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($Path, "$json`n", [System.Text.Encoding]::UTF8)
}

function Get-Number {
    param(
        [object]$Object,
        [string]$Name
    )

    $property = $Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if ($null -eq $property) {
        throw "Missing numeric property '$Name'."
    }

    return [double]$property.Value
}

function Get-IntNumber {
    param(
        [object]$Object,
        [string]$Name
    )

    return [int](Get-Number $Object $Name)
}

function New-MetricDelta {
    param(
        [object]$BaselineMetrics,
        [object]$CurrentMetrics,
        [string]$Name
    )

    $baselineValue = Get-Number $BaselineMetrics $Name
    $currentValue = Get-Number $CurrentMetrics $Name
    return [ordered]@{
        baseline = [Math]::Round($baselineValue, 4)
        current = [Math]::Round($currentValue, 4)
        delta = [Math]::Round(($currentValue - $baselineValue), 4)
    }
}

if ($Strategy -ne "keyword") {
    throw "retrieval-regression-report.ps1 is CI-safe and currently supports only Strategy=keyword. Optional vector / rerank strategies must be reported with skip reason unless a later ticket enables them."
}

if (-not (Test-Path -LiteralPath $evalSmokeScript)) {
    throw "Missing retrieval eval smoke script at $evalSmokeScript"
}

$resolvedDatasetPath = (Resolve-Path -LiteralPath $DatasetPath).Path
$resolvedMetadataPath = (Resolve-Path -LiteralPath $MetadataPath).Path
$resolvedBaselinePath = (Resolve-Path -LiteralPath $BaselinePath).Path

Write-Host "Retrieval regression report smoke"
Write-Host "Strategy: $Strategy"
Write-Host "Dataset: $resolvedDatasetPath"
Write-Host "Baseline: $resolvedBaselinePath"
Write-Host "Current result: $CurrentResultPath"
Write-Host "Report output: $OutputPath"

& $evalSmokeScript -DatasetPath $resolvedDatasetPath -OutputPath $CurrentResultPath
if (-not $?) {
    throw "Retrieval eval smoke failed before regression report generation."
}

$metadata = Read-JsonFile $resolvedMetadataPath
$baseline = Read-JsonFile $resolvedBaselinePath
$current = Read-JsonFile $CurrentResultPath

$datasetFile = Split-Path -Leaf $resolvedDatasetPath
$datasetMetadata = @($metadata.datasets | Where-Object { $_.dataset_file -eq $datasetFile }) | Select-Object -First 1
if ($null -eq $datasetMetadata) {
    throw "No golden dataset metadata found for dataset file '$datasetFile'."
}

if ($baseline.strategy -ne $Strategy) {
    throw "Baseline strategy '$($baseline.strategy)' does not match current strategy '$Strategy'."
}

if ($current.strategy -ne $Strategy) {
    throw "Current result strategy '$($current.strategy)' does not match requested strategy '$Strategy'."
}

$metricNames = @(
    "hit_rate_at_k",
    "mrr_at_k",
    "recall_at_k",
    "average_latency_ms",
    "failure_count",
    "fallback_count",
    "trace_metadata_count"
)

$metricDelta = [ordered]@{}
foreach ($metricName in $metricNames) {
    $metricDelta[$metricName] = New-MetricDelta $baseline.metrics $current.summary $metricName
}

$thresholds = $baseline.thresholds
$maxMetricDrop = Get-Number $thresholds "max_metric_drop"
$maxFailureCountDelta = Get-IntNumber $thresholds "max_failure_count_delta"
$warnFallbackCountDelta = Get-IntNumber $thresholds "warn_fallback_count_delta"
$warnLatencyRatio = Get-Number $thresholds "warn_latency_ratio"
$warnTraceMetadataDrop = Get-IntNumber $thresholds "warn_trace_metadata_drop"

$failReasons = @()
$warnReasons = @()

foreach ($metricName in @("hit_rate_at_k", "mrr_at_k", "recall_at_k")) {
    if ($metricDelta[$metricName].delta -lt (-1 * $maxMetricDrop)) {
        $failReasons += "$metricName dropped by $($metricDelta[$metricName].delta), below allowed threshold -$maxMetricDrop."
    }
}

$failureDelta = (Get-IntNumber $current.summary "failure_count") - (Get-IntNumber $baseline.metrics "failure_count")
if ($failureDelta -gt $maxFailureCountDelta) {
    $failReasons += "failure_count increased by $failureDelta, above allowed threshold $maxFailureCountDelta."
}

$fallbackDelta = (Get-IntNumber $current.summary "fallback_count") - (Get-IntNumber $baseline.metrics "fallback_count")
if ($fallbackDelta -gt $warnFallbackCountDelta) {
    $warnReasons += "fallback_count increased by $fallbackDelta; inspect provider availability and skip reason."
}

$baselineLatency = Get-Number $baseline.metrics "average_latency_ms"
$currentLatency = Get-Number $current.summary "average_latency_ms"
if ($baselineLatency -gt 0 -and $currentLatency -gt ($baselineLatency * $warnLatencyRatio)) {
    $warnReasons += "average_latency_ms increased from $baselineLatency to $currentLatency; threshold ratio is $warnLatencyRatio."
}

$traceMetadataDrop = (Get-IntNumber $baseline.metrics "trace_metadata_count") - (Get-IntNumber $current.summary "trace_metadata_count")
if ($traceMetadataDrop -gt $warnTraceMetadataDrop) {
    $warnReasons += "trace_metadata_count dropped by $traceMetadataDrop; inspect retrieval trace coverage."
}

$gateStatus = "pass"
if ($failReasons.Count -gt 0) {
    $gateStatus = "fail"
}
elseif ($warnReasons.Count -gt 0) {
    $gateStatus = "warn"
}

$providerAvailability = [ordered]@{}
foreach ($property in $baseline.provider_availability.PSObject.Properties) {
    $providerAvailability[$property.Name] = $property.Value
}

$report = [ordered]@{
    report_schema_version = "retrieval_regression_report_v1"
    created_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    dataset = [ordered]@{
        dataset_file = $datasetFile
        dataset_id = $datasetMetadata.dataset_id
        dataset_version = $datasetMetadata.dataset_version
        metadata_version = $metadata.metadata_version
        metadata_path = $resolvedMetadataPath
    }
    strategy = $Strategy
    provider_availability = $providerAvailability
    skip_reason = ""
    baseline = [ordered]@{
        baseline_id = $baseline.baseline_id
        baseline_path = $resolvedBaselinePath
        metrics = $baseline.metrics
    }
    current = [ordered]@{
        run_id = $current.run_id
        result_path = (Resolve-Path -LiteralPath $CurrentResultPath).Path
        metrics = $current.summary
    }
    comparison = [ordered]@{
        metric_delta = $metricDelta
        thresholds = $thresholds
        regression_gate = $gateStatus
        warn_reasons = $warnReasons
        fail_reasons = $failReasons
    }
    local_usage = "powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\retrieval-regression-report.ps1"
    ci_usage = "Run the same command after backend dependencies are installed. The default keyword report does not require Qdrant, Ollama, FastEmbed or GPU runtime."
}

Write-JsonFile $OutputPath $report

Write-Host "Retrieval regression report written: $OutputPath"
Write-Host "dataset version: $($datasetMetadata.dataset_version)"
Write-Host "strategy: $Strategy"
Write-Host "provider availability:"
$providerAvailability | ConvertTo-Json -Depth 8
Write-Host "baseline vs current metric delta:"
$metricDelta | ConvertTo-Json -Depth 8
Write-Host "regression gate: $gateStatus"

if ($warnReasons.Count -gt 0) {
    Write-Host "warn reasons:"
    $warnReasons | ConvertTo-Json -Depth 8
}

if ($failReasons.Count -gt 0) {
    $failReasons | ConvertTo-Json -Depth 8
    throw "Retrieval regression gate failed. See report at $OutputPath"
}
