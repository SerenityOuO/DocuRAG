param(
    [string]$GoldenLabelsPath = "",
    [string]$ParserResultsPath = "",
    [string]$ReportPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($GoldenLabelsPath)) {
    $GoldenLabelsPath = Join-Path $repoRoot "sample-data/eval/parser-golden-labels.json"
}

if ([string]::IsNullOrWhiteSpace($ParserResultsPath)) {
    $ParserResultsPath = Join-Path $repoRoot "sample-data/eval/parser-field-results.json"
}

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $repoRoot ".tmp/parser-field-accuracy-report.json"
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

function ConvertTo-ObjectArray {
    param([object]$Value)

    if ($null -eq $Value) {
        return @()
    }

    return @($Value)
}

function Get-PropertyValue {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $null
    }

    $property = $Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if ($null -eq $property) {
        return $null
    }

    return $property.Value
}

function Get-RequiredString {
    param(
        [object]$Object,
        [string]$Name
    )

    $value = Get-PropertyValue $Object $Name
    if ($null -eq $value -or [string]::IsNullOrWhiteSpace([string]$value)) {
        throw "Missing required string '$Name'."
    }

    return [string]$value
}

function New-FieldKey {
    param(
        [string]$DocumentId,
        [string]$FieldName
    )

    return "$DocumentId::$FieldName"
}

function ConvertTo-NormalizedValue {
    param([object]$Value)

    if ($null -eq $Value) {
        return ""
    }

    $text = ([string]$Value).Trim()
    if ([string]::IsNullOrWhiteSpace($text)) {
        return ""
    }

    $candidate = $text.ToLowerInvariant()
    $candidate = $candidate -replace "^(usd|twd|ntd|nt\$)\s*", ""
    $candidate = $candidate -replace "\s*(usd|twd|ntd)$", ""
    $candidate = $candidate -replace ",", ""

    $number = 0.0
    if (
        [double]::TryParse(
            $candidate,
            [System.Globalization.NumberStyles]::Float,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [ref]$number
        )
    ) {
        return $number.ToString("0.####", [System.Globalization.CultureInfo]::InvariantCulture)
    }

    return (($text -replace "\s+", " ").Trim()).ToLowerInvariant()
}

function Get-ConfidenceBucket {
    param([object]$Confidence)

    if ($null -eq $Confidence) {
        return "unknown"
    }

    $number = [double]$Confidence
    if ($number -ge 0.8) {
        return "high"
    }

    if ($number -ge 0.5) {
        return "medium"
    }

    return "low"
}

function Add-Count {
    param(
        [hashtable]$Table,
        [string]$Name
    )

    $key = $Name
    if ([string]::IsNullOrWhiteSpace($key)) {
        $key = "none"
    }

    if (-not $Table.ContainsKey($key)) {
        $Table[$key] = 0
    }

    $Table[$key] += 1
}

function ConvertTo-RepoRelativePath {
    param([string]$Path)

    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    if ($resolvedPath.StartsWith($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return (($resolvedPath.Substring($repoRoot.Length) -replace "^[\\/]+", "") -replace "\\", "/")
    }

    return $resolvedPath
}

function ConvertTo-OrderedCounts {
    param([hashtable]$Table)

    $ordered = [ordered]@{}
    foreach ($key in @($Table.Keys | Sort-Object)) {
        $ordered[$key] = $Table[$key]
    }

    return $ordered
}

Write-Host "Parser field accuracy smoke"
Write-Host "Golden labels: $GoldenLabelsPath"
Write-Host "Parser results: $ParserResultsPath"
Write-Host "Report: $ReportPath"

$goldenLabels = Read-JsonFile $GoldenLabelsPath
$parserResults = Read-JsonFile $ParserResultsPath

if ((Get-RequiredString $goldenLabels "schema_version") -ne "parser_golden_labels_v1") {
    throw "Golden labels must use schema_version parser_golden_labels_v1."
}

if ((Get-RequiredString $parserResults "schema_version") -ne "parser_field_results_v1") {
    throw "Parser results must use schema_version parser_field_results_v1."
}

$parserResultIndex = @{}
foreach ($parserResult in @(ConvertTo-ObjectArray (Get-PropertyValue $parserResults "parser_results"))) {
    $documentId = Get-RequiredString $parserResult "document_id"
    $parserResultIndex[$documentId] = $parserResult
}

$fieldResults = @()
$documentStates = @{}
$parserSourceCounts = @{}
$confidenceBucketCounts = @{}
$fallbackReasonCounts = @{}

$matchedFieldCount = 0
$exactMatchCount = 0
$normalizedMatchCount = 0
$missingFieldCount = 0
$wrongValueCount = 0
$evidenceMismatchCount = 0

foreach ($label in @(ConvertTo-ObjectArray (Get-PropertyValue $goldenLabels "labels"))) {
    $documentId = Get-RequiredString $label "document_id"
    $fieldName = Get-RequiredString $label "field_name"
    $expectedValue = Get-PropertyValue $label "corrected_value"
    $parserResult = $parserResultIndex[$documentId]
    $field = $null

    if ($null -ne $parserResult) {
        $fields = Get-PropertyValue $parserResult "fields"
        $field = Get-PropertyValue $fields $fieldName
    }

    $parserValue = Get-PropertyValue $field "value"
    $confidence = Get-PropertyValue $field "confidence"
    $fieldParserSource = Get-PropertyValue $field "parser_source"
    if ([string]::IsNullOrWhiteSpace([string]$fieldParserSource) -and $null -ne $parserResult) {
        $fieldParserSource = Get-PropertyValue $parserResult "parser_source"
    }

    $fallbackReason = Get-PropertyValue $field "fallback_reason"
    $expectedNormalized = ConvertTo-NormalizedValue $expectedValue
    $parserNormalized = ConvertTo-NormalizedValue $parserValue
    $expectedRaw = ""
    if ($null -ne $expectedValue) {
        $expectedRaw = ([string]$expectedValue).Trim()
    }
    $parserRaw = ""
    if ($null -ne $parserValue) {
        $parserRaw = ([string]$parserValue).Trim()
    }

    $comparisonResult = "wrong_value"
    if ([string]::IsNullOrWhiteSpace($parserRaw)) {
        $comparisonResult = "missing_field"
        $missingFieldCount += 1
    }
    elseif ($parserRaw -eq $expectedRaw) {
        $comparisonResult = "exact_match"
        $matchedFieldCount += 1
        $exactMatchCount += 1
    }
    elseif ($parserNormalized -eq $expectedNormalized -and -not [string]::IsNullOrWhiteSpace($parserNormalized)) {
        $comparisonResult = "normalized_match"
        $matchedFieldCount += 1
        $normalizedMatchCount += 1
    }
    else {
        $wrongValueCount += 1
    }

    $evidenceStatus = "available"
    if (@("evidence_unmatched", "evidence_unavailable") -contains [string]$fallbackReason) {
        $evidenceStatus = [string]$fallbackReason
        $evidenceMismatchCount += 1
    }

    Add-Count $parserSourceCounts ([string]$fieldParserSource)
    Add-Count $confidenceBucketCounts (Get-ConfidenceBucket $confidence)
    Add-Count $fallbackReasonCounts ([string]$fallbackReason)

    if (-not $documentStates.ContainsKey($documentId)) {
        $documentStates[$documentId] = [ordered]@{
            total = 0
            matched = 0
            missing = 0
            wrong = 0
        }
    }

    $documentStates[$documentId].total += 1
    if (@("exact_match", "normalized_match") -contains $comparisonResult) {
        $documentStates[$documentId].matched += 1
    }
    elseif ($comparisonResult -eq "missing_field") {
        $documentStates[$documentId].missing += 1
    }
    else {
        $documentStates[$documentId].wrong += 1
    }

    $fieldResults += [ordered]@{
        document_id = $documentId
        filename = Get-PropertyValue $label "filename"
        field_name = $fieldName
        expected_value = $expectedValue
        parser_value = $parserValue
        comparison_result = $comparisonResult
        expected_normalized = $expectedNormalized
        parser_normalized = $parserNormalized
        parser_source = $fieldParserSource
        fallback_reason = $fallbackReason
        confidence = $confidence
        confidence_bucket = Get-ConfidenceBucket $confidence
        evidence_status = $evidenceStatus
        correction_version = Get-PropertyValue $label "version"
    }
}

$sampleCount = $fieldResults.Count
if ($sampleCount -eq 0) {
    throw "No parser field labels were available for evaluation."
}

$documentCount = $documentStates.Count
$documentMatchedCount = 0
foreach ($documentId in $documentStates.Keys) {
    $state = $documentStates[$documentId]
    if ($state.total -gt 0 -and $state.matched -eq $state.total -and $state.missing -eq 0 -and $state.wrong -eq 0) {
        $documentMatchedCount += 1
    }
}

$fieldAccuracy = [Math]::Round(($matchedFieldCount / $sampleCount), 4)
$documentAccuracy = 0.0
if ($documentCount -gt 0) {
    $documentAccuracy = [Math]::Round(($documentMatchedCount / $documentCount), 4)
}

$report = [ordered]@{
    schema_version = "parser_field_accuracy_report_v1"
    evaluation_mode = "deterministic_parser_vs_human_golden_labels"
    dataset = [ordered]@{
        golden_labels_path = ConvertTo-RepoRelativePath $GoldenLabelsPath
        parser_results_path = ConvertTo-RepoRelativePath $ParserResultsPath
        label_count = $sampleCount
        document_count = $documentCount
    }
    summary = [ordered]@{
        field_accuracy = $fieldAccuracy
        document_accuracy = $documentAccuracy
        sample_count = $sampleCount
        document_count = $documentCount
        matched_field_count = $matchedFieldCount
        exact_match_count = $exactMatchCount
        normalized_match_count = $normalizedMatchCount
        missing_field_count = $missingFieldCount
        wrong_value_count = $wrongValueCount
        evidence_mismatch_count = $evidenceMismatchCount
    }
    parser_source_counts = ConvertTo-OrderedCounts $parserSourceCounts
    confidence_bucket_counts = ConvertTo-OrderedCounts $confidenceBucketCounts
    fallback_reason_counts = ConvertTo-OrderedCounts $fallbackReasonCounts
    field_results = $fieldResults
    boundary = "Parser field accuracy compares structured parser output to human golden labels. It is not RAG retrieval eval, LLM-as-judge, model training, production analytics dashboard or automatic parser correction."
    local_usage = "powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\parser-field-accuracy-smoke.ps1"
}

Write-JsonFile $ReportPath $report

Write-Host "Parser field accuracy report written: $ReportPath"
Write-Host "summary:"
$report.summary | ConvertTo-Json -Depth 8

if ($missingFieldCount -lt 0 -or $wrongValueCount -lt 0 -or $evidenceMismatchCount -lt 0) {
    throw "Parser field accuracy counters are invalid."
}

Write-Host "Parser field accuracy smoke passed."
