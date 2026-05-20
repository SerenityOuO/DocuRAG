Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$failed = 0

function Write-Result {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    if ($Passed) {
        Write-Host "[PASS] $Name - $Detail"
    }
    else {
        Write-Host "[FAIL] $Name - $Detail"
        $script:failed += 1
    }
}

function Invoke-CmdLine {
    param([string]$CommandLine)

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $process.StartInfo.FileName = "cmd.exe"
    $process.StartInfo.Arguments = "/d /c chcp 65001 >nul & $CommandLine"
    $process.StartInfo.RedirectStandardOutput = $true
    $process.StartInfo.RedirectStandardError = $true
    $process.StartInfo.UseShellExecute = $false
    $process.StartInfo.CreateNoWindow = $true
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    $output = ($stdout + $stderr).Trim()

    return @{
        ExitCode = $process.ExitCode
        Output = $output
    }
}

function Invoke-CheckLine {
    param(
        [string]$Name,
        [string]$CommandLine
    )

    $result = Invoke-CmdLine $CommandLine
    if ($result.ExitCode -eq 0) {
        Write-Result $Name $true $result.Output
        return $true
    }

    $detail = $result.Output
    if ($CommandLine -eq "where python") {
        $detail = "python.exe not found in PATH by where.exe"
    }
    elseif ($CommandLine -eq "where py") {
        $detail = "py launcher not found in PATH"
    }
    elseif ($CommandLine -eq "python --version") {
        $detail = "python command cannot execute; check for broken WindowsApps alias or missing Python install"
    }
    elseif ($CommandLine -like "py *") {
        $detail = "py launcher is not available"
    }
    elseif ($CommandLine -eq "where docker") {
        $detail = "docker.exe not found in PATH by where.exe"
    }
    elseif ($CommandLine -like "docker *") {
        $detail = "Docker CLI is not available"
    }

    Write-Result $Name $false ("exit code " + $result.ExitCode + "; " + $detail)
    return $false
}

Write-Host "DocuRAG local development environment check"
Write-Host ""

$pythonWhereOk = Invoke-CheckLine "where python" "where python"
$pyWhereOk = Invoke-CheckLine "where py" "where py"

$pythonOk = Invoke-CheckLine "python --version" "python --version"
$pyOk = Invoke-CheckLine "py --version" "py --version"
Invoke-CheckLine "py -0p" "py -0p" | Out-Null

if ($pyOk) {
    Invoke-CheckLine "pip via py" "py -m pip --version" | Out-Null
}
elseif ($pythonOk) {
    Invoke-CheckLine "pip via python" "python -m pip --version" | Out-Null
}
else {
    Write-Result "pip" $false "Python is not available"
}

Invoke-CheckLine "where docker" "where docker" | Out-Null
$dockerOk = Invoke-CheckLine "docker --version" "docker --version"
if ($dockerOk) {
    Invoke-CheckLine "docker compose version" "docker compose version" | Out-Null
}
else {
    Write-Result "docker compose version" $false "Docker CLI is not available"
}

Write-Host ""
if ($failed -gt 0) {
    Write-Host "Environment check failed with $failed issue(s). See docs/LOCAL_DEV_SETUP.md for fixes."
    exit 1
}

Write-Host "Environment check passed."
exit 0
