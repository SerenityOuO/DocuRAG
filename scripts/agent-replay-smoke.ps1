param(
    [string]$ArtifactPath = "",
    [string]$ReportPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($ArtifactPath)) {
    $ArtifactPath = Join-Path $repoRoot "sample-data/eval/agent-replay-sample.json"
}

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $ReportPath = Join-Path $repoRoot ".tmp/agent-replay-report.json"
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

function Get-PropertyValue {
    param(
        [object]$Object,
        [string]$Name
    )

    $property = $Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if ($null -eq $property) {
        throw "Missing required property '$Name'."
    }

    return $property.Value
}

function Get-OptionalString {
    param(
        [object]$Object,
        [string]$Name
    )

    $property = $Object.PSObject.Properties | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if ($null -eq $property -or $null -eq $property.Value) {
        return ""
    }

    return [string]$property.Value
}

function Get-RequiredString {
    param(
        [object]$Object,
        [string]$Name
    )

    $value = Get-OptionalString $Object $Name
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required string '$Name' is empty."
    }

    return $value
}

function ConvertTo-ObjectArray {
    param([object]$Value)

    if ($null -eq $Value) {
        return @()
    }

    return @($Value)
}

function Add-NonEmptyString {
    param(
        [object[]]$Values,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Values
    }

    return $Values + $Value
}

Write-Host "Agent replay smoke"
Write-Host "Artifact: $ArtifactPath"

$artifact = Read-JsonFile $ArtifactPath
$schemaVersion = Get-RequiredString $artifact "schema_version"
$replayId = Get-RequiredString $artifact "replay_id"
$sourceRunId = Get-RequiredString $artifact "source_run_id"
$policySnapshotId = Get-RequiredString $artifact "policy_snapshot_id"
$replayMode = Get-RequiredString $artifact "replay_mode"
$finalAnswerSource = Get-RequiredString $artifact "final_answer_source"

if ($schemaVersion -ne "agent_replay_v1") {
    throw "Unsupported Agent replay schema_version '$schemaVersion'."
}

if ($replayMode -ne "inspection_only_no_tool_execution") {
    throw "Replay mode must be inspection_only_no_tool_execution. Got '$replayMode'."
}

$planSteps = @(ConvertTo-ObjectArray (Get-PropertyValue $artifact "plan_steps"))
$toolCalls = @(ConvertTo-ObjectArray (Get-PropertyValue $artifact "tool_calls"))
$toolPolicies = @(ConvertTo-ObjectArray (Get-PropertyValue $artifact "tool_policy_snapshot"))
$citations = @(ConvertTo-ObjectArray (Get-PropertyValue $artifact "citations"))
$finalAnswer = Get-PropertyValue $artifact "final_answer"

if ($planSteps.Count -eq 0) {
    throw "Agent replay artifact has no plan_steps."
}

if ($toolCalls.Count -eq 0) {
    throw "Agent replay artifact has no tool_calls."
}

if ($toolPolicies.Count -eq 0) {
    throw "Agent replay artifact has no tool_policy_snapshot."
}

$plannedTools = @()
foreach ($step in $planSteps) {
    $toolName = Get-OptionalString $step "tool_name"
    if (-not [string]::IsNullOrWhiteSpace($toolName)) {
        $plannedTools += $toolName
    }
}

$calledTools = @()
$observationCount = 0
$traceMetadataCount = 0
$fallbackReasons = @()
$validToolStatusCount = 0
$toolCitationCount = 0

foreach ($toolCall in $toolCalls) {
    $calledTools += (Get-RequiredString $toolCall "tool_name")
    $status = Get-RequiredString $toolCall "status"
    if (@("completed", "failed") -contains $status) {
        $validToolStatusCount += 1
    }

    if (-not [string]::IsNullOrWhiteSpace((Get-OptionalString $toolCall "observation_summary"))) {
        $observationCount += 1
    }

    $fallbackReasons = Add-NonEmptyString $fallbackReasons (Get-OptionalString $toolCall "fallback_reason")

    $traceMetadata = Get-PropertyValue $toolCall "trace_metadata"
    if (
        -not [string]::IsNullOrWhiteSpace((Get-OptionalString $traceMetadata "permission_decision")) -and
        -not [string]::IsNullOrWhiteSpace((Get-OptionalString $traceMetadata "tool_tier"))
    ) {
        $traceMetadataCount += 1
    }

    $toolCitationCount += @(ConvertTo-ObjectArray (Get-PropertyValue $toolCall "citations")).Count
}

foreach ($step in $planSteps) {
    $fallbackReasons = Add-NonEmptyString $fallbackReasons (Get-OptionalString $step "fallback_reason")
}

$fallbackReasons = Add-NonEmptyString $fallbackReasons (Get-OptionalString $artifact "fallback_reason")
$fallbackReasons = Add-NonEmptyString $fallbackReasons (Get-OptionalString $finalAnswer "fallback_reason")
$fallbackReasons = @($fallbackReasons | Select-Object -Unique)

$toolSequenceMatches = (($plannedTools -join ",") -eq ($calledTools -join ","))
$toolCorrectnessStatus = "fail"
if ($toolSequenceMatches -and $validToolStatusCount -eq $toolCalls.Count -and $observationCount -eq $toolCalls.Count) {
    $toolCorrectnessStatus = "pass"
}

$unsafePolicyCount = 0
$approvalViolationCount = 0
foreach ($policy in $toolPolicies) {
    $toolTier = Get-RequiredString $policy "tool_tier"
    $sideEffectPolicy = Get-RequiredString $policy "side_effect_policy"
    $permissionDecision = Get-RequiredString $policy "permission_decision"
    $approvalState = Get-RequiredString $policy "approval_state"
    $approvalRequired = [bool](Get-PropertyValue $policy "approval_required")

    if ($toolTier -eq "destructive" -or $sideEffectPolicy -eq "prohibited") {
        $unsafePolicyCount += 1
    }

    if ($approvalRequired -and $approvalState -ne "approved" -and $permissionDecision -eq "allowed") {
        $approvalViolationCount += 1
    }
}

$permissionComplianceStatus = "fail"
if ($unsafePolicyCount -eq 0 -and $approvalViolationCount -eq 0) {
    $permissionComplianceStatus = "pass"
}

$evidenceCoverageStatus = "fail"
if ($traceMetadataCount -eq $toolCalls.Count -and $observationCount -eq $toolCalls.Count -and ($citations.Count + $toolCitationCount) -gt 0) {
    $evidenceCoverageStatus = "pass"
}

$fallbackReasonStatus = "fail"
if ($fallbackReasons.Count -gt 0) {
    $fallbackReasonStatus = "pass"
}

$finalAnswerText = Get-RequiredString $finalAnswer "text"
$groundednessStatus = "fail"
if (
    -not [string]::IsNullOrWhiteSpace($finalAnswerText) -and
    ($citations.Count + $toolCitationCount) -gt 0 -and
    $finalAnswerSource -eq "tool_observation_and_citations"
) {
    $groundednessStatus = "pass"
}

$dimensions = @(
    [ordered]@{
        name = "tool correctness"
        status = $toolCorrectnessStatus
        notes = "planned_tools=$($plannedTools -join ','); called_tools=$($calledTools -join ','); observations=$observationCount/$($toolCalls.Count)"
    },
    [ordered]@{
        name = "permission compliance"
        status = $permissionComplianceStatus
        notes = "unsafe_policy_count=$unsafePolicyCount; approval_violation_count=$approvalViolationCount; replay_mode=$replayMode"
    },
    [ordered]@{
        name = "evidence coverage"
        status = $evidenceCoverageStatus
        notes = "run_citations=$($citations.Count); tool_citations=$toolCitationCount; trace_metadata=$traceMetadataCount/$($toolCalls.Count)"
    },
    [ordered]@{
        name = "fallback reason"
        status = $fallbackReasonStatus
        notes = "fallback_reasons=$($fallbackReasons -join ',')"
    },
    [ordered]@{
        name = "groundedness"
        status = $groundednessStatus
        notes = "final_answer_source=$finalAnswerSource; deterministic note only, no LLM-as-judge"
    }
)

$failedDimensions = @($dimensions | Where-Object { $_.status -ne "pass" })
$summaryStatus = "pass"
if ($failedDimensions.Count -gt 0) {
    $summaryStatus = "fail"
}

$report = [ordered]@{
    schema_version = "agent_replay_eval_report_v1"
    replay_id = $replayId
    source_run_id = $sourceRunId
    policy_snapshot_id = $policySnapshotId
    replay_mode = $replayMode
    status = $summaryStatus
    destructive_tools_executed = $false
    external_side_effect_tools_executed = $false
    dimensions = $dimensions
    replay = [ordered]@{
        planned_tools = $plannedTools
        tool_calls = $calledTools
        observations = $observationCount
        citations = $citations.Count
        fallback_reasons = $fallbackReasons
        final_answer_source = $finalAnswerSource
    }
}

Write-JsonFile $ReportPath $report
Write-Host "Report: $ReportPath"

if ($summaryStatus -ne "pass") {
    throw "Agent replay smoke failed. Failed dimensions: $($failedDimensions.name -join ', ')"
}

Write-Host "Agent replay smoke passed: $replayId"
