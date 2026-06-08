param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$SamplePath = "",
    [string]$ExpectedVersion = "0.38.0",
    [switch]$RequirePlannerFallback
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($SamplePath)) {
    $SamplePath = Join-Path $repoRoot "sample-data/documents/mock-invoice-aurora.txt"
}

$resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path

function Assert-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

function Get-ErrorStatusCode {
    param([object]$ErrorRecord)

    $response = $ErrorRecord.Exception.Response
    if ($null -eq $response) {
        return $null
    }

    if ($response.PSObject.Properties.Name -contains "StatusCode") {
        $statusCode = $response.StatusCode
        if ($statusCode -is [int]) {
            return $statusCode
        }
        if ($statusCode.PSObject.Properties.Name -contains "value__") {
            return [int]$statusCode.value__
        }
    }

    return $null
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
            throw "Upload failed with curl exit code $LASTEXITCODE."
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

function New-AgentBody {
    param([string]$DocumentId)

    return @{
        task = "Summarize invoice fields and cite payment terms."
        document_id = $DocumentId
        query = "payment terms"
        top_k = 3
    } | ConvertTo-Json
}

Write-Host "Agent runtime smoke"
Write-Host "API: $ApiBaseUrl"

$health = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/health"
Assert-Condition ($health.status -eq "ok") "Expected /health status ok."
Assert-Condition ($health.version -eq $ExpectedVersion) "Expected /health version $ExpectedVersion. Got $($health.version)."
Write-Host "Health OK: version $($health.version)"

$authHeaders = @{}
$viewerHeaders = $null
$authState = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/auth/me"
if ($authState.auth_mode -eq "demo") {
    $adminBody = @{
        username = "admin"
        password = "demo-admin-pass"
    } | ConvertTo-Json
    $adminLogin = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/auth/login" -ContentType "application/json" -Body $adminBody
    Assert-Condition ($adminLogin.user.role -eq "admin") "Demo auth admin login did not return admin role."
    $authHeaders = @{
        Authorization = "Bearer $($adminLogin.access_token)"
    }

    $viewerBody = @{
        username = "viewer"
        password = "demo-viewer-pass"
    } | ConvertTo-Json
    $viewerLogin = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/auth/login" -ContentType "application/json" -Body $viewerBody
    Assert-Condition ($viewerLogin.user.role -eq "viewer") "Demo auth viewer login did not return viewer role."
    $viewerHeaders = @{
        Authorization = "Bearer $($viewerLogin.access_token)"
    }
    Write-Host "Demo auth OK: admin and viewer login"
}
else {
    Write-Host "Demo auth disabled; viewer forbidden API check skipped."
}

$upload = Invoke-FileUpload "$ApiBaseUrl/documents/upload" $resolvedSamplePath "text/plain" $authHeaders
Assert-Condition (-not [string]::IsNullOrWhiteSpace($upload.document_id)) "Upload did not return document_id."
Assert-Condition ($upload.processing.indexing -eq "completed") "Direct text upload did not complete local indexing."

$parser = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/documents/$($upload.document_id)/parse" -Headers $authHeaders
Assert-Condition ($parser.status -eq "parsed") "Parser did not return parsed status."
Assert-Condition ($parser.trace_metadata.fallback_chain -eq "vlm_invoice -> deterministic_invoice") "Expected parser fallback chain to deterministic invoice for text input."
Write-Host "Parser fallback OK: $($parser.trace_metadata.fallback_chain)"

$agentBody = New-AgentBody $upload.document_id
$agentRun = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/agent/run" -ContentType "application/json" -Body $agentBody -Headers $authHeaders

Assert-Condition ($agentRun.status -eq "completed") "Agent run did not complete. Got '$($agentRun.status)'."
Assert-Condition ($agentRun.trace.tool_policy -eq "allowlisted_read_only") "Agent tool policy was '$($agentRun.trace.tool_policy)'; expected allowlisted_read_only."
Assert-Condition ($agentRun.trace.permission_decision -eq "allowed") "Agent permission decision was '$($agentRun.trace.permission_decision)'; expected allowed."
Assert-Condition ($agentRun.trace.permission_reason -eq "all_planned_tools_allowed") "Agent permission reason was '$($agentRun.trace.permission_reason)'; expected all_planned_tools_allowed."
Assert-Condition ($agentRun.trace.tool_tiers -eq "read-only") "Agent tool tier trace was '$($agentRun.trace.tool_tiers)'; expected read-only."
Assert-Condition ($agentRun.trace.side_effect_policy -eq "no_side_effects") "Agent side-effect policy was '$($agentRun.trace.side_effect_policy)'; expected no_side_effects."
Assert-Condition ($agentRun.trace.human_confirmation_required -eq "not_required") "Agent human confirmation trace was '$($agentRun.trace.human_confirmation_required)'; expected not_required."
Assert-Condition ($agentRun.tool_calls.Count -eq 3) "Agent run expected 3 tool calls. Got $($agentRun.tool_calls.Count)."

foreach ($toolCall in $agentRun.tool_calls) {
    Assert-Condition ($toolCall.trace_metadata.permission_decision -eq "allowed") "Tool $($toolCall.tool_name) permission decision was '$($toolCall.trace_metadata.permission_decision)'; expected allowed."
    Assert-Condition ($toolCall.trace_metadata.tool_tier -eq "read-only") "Tool $($toolCall.tool_name) tier was '$($toolCall.trace_metadata.tool_tier)'; expected read-only."
    Assert-Condition ($toolCall.trace_metadata.side_effect_policy -eq "no_side_effects") "Tool $($toolCall.tool_name) side-effect policy was '$($toolCall.trace_metadata.side_effect_policy)'; expected no_side_effects."
    Assert-Condition ($toolCall.trace_metadata.human_confirmation_required -eq "not_required") "Tool $($toolCall.tool_name) human confirmation was '$($toolCall.trace_metadata.human_confirmation_required)'; expected not_required."
    Assert-Condition ($toolCall.trace_metadata.destructive -eq "false") "Tool $($toolCall.tool_name) reported destructive=$($toolCall.trace_metadata.destructive); expected false."
}

if ($RequirePlannerFallback) {
    Assert-Condition ($agentRun.trace.planner -eq "deterministic") "Planner after fallback was '$($agentRun.trace.planner)'; expected deterministic."
    Assert-Condition ($agentRun.trace.planner_attempted_provider -eq "llm_planner") "Planner attempted provider was '$($agentRun.trace.planner_attempted_provider)'; expected llm_planner."
    Assert-Condition ($agentRun.trace.planner_status -eq "fallback") "Planner status was '$($agentRun.trace.planner_status)'; expected fallback."
    Assert-Condition (@("timeout", "unavailable", "invalid") -contains $agentRun.trace.plan_validation_status) "Planner validation status was '$($agentRun.trace.plan_validation_status)'; expected timeout, unavailable, or invalid."
    Assert-Condition ($agentRun.trace.planner_fallback_reason -match "^llm_planner_") "Planner fallback reason was '$($agentRun.trace.planner_fallback_reason)'; expected llm_planner_*."
    Write-Host "Planner fallback OK: $($agentRun.trace.planner_fallback_reason)"
}
else {
    Assert-Condition (@("completed", "fallback") -contains $agentRun.trace.planner_status) "Planner status was '$($agentRun.trace.planner_status)'; expected completed or fallback."
    Write-Host "Planner trace OK: $($agentRun.trace.planner_status)"
}

if ($null -ne $viewerHeaders) {
    try {
        Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/agent/run" -ContentType "application/json" -Body $agentBody -Headers $viewerHeaders | Out-Null
        throw "Viewer Agent run unexpectedly succeeded."
    }
    catch {
        $statusCode = Get-ErrorStatusCode $_
        Assert-Condition ($statusCode -eq 403) "Viewer Agent run expected HTTP 403. Got $statusCode."
        Write-Host "Viewer forbidden OK: HTTP $statusCode"
    }
}

$lookup = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/agent/runs/$($agentRun.run_id)" -Headers $authHeaders
Assert-Condition ($lookup.run_id -eq $agentRun.run_id) "Agent lookup did not return the saved run."
Assert-Condition ($lookup.trace.permission_decision -eq "allowed") "Agent lookup did not preserve permission decision trace."

Write-Host "Agent permission trace OK: $($agentRun.trace.permission_decisions)"
Write-Host "Agent runtime smoke passed."
