Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$failed = 0
$warnings = 0

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

function Write-WarnResult {
    param(
        [string]$Name,
        [string]$Detail
    )

    Write-Host "[WARN] $Name - $Detail"
    $script:warnings += 1
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
    elseif ($CommandLine -eq "node --version") {
        $detail = "Node.js is not available"
    }
    elseif ($CommandLine -eq "npm.cmd --version") {
        $detail = "npm.cmd is not available"
    }
    elseif ($CommandLine -like "docker *") {
        $detail = "Docker CLI is not available"
    }

    Write-Result $Name $false ("exit code " + $result.ExitCode + "; " + $detail)
    return $false
}

function Invoke-DiagnosticLine {
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

    Write-WarnResult $Name ("exit code " + $result.ExitCode + "; " + $detail)
    return $false
}

function Find-PythonFromPip {
    $pipCommand = Get-Command pip -ErrorAction SilentlyContinue
    if ($null -eq $pipCommand) {
        return $null
    }

    $pipPath = $pipCommand.Source
    $result = Invoke-CmdLine "`"$pipPath`" --version"
    if ($result.ExitCode -ne 0) {
        return $null
    }

    if ($result.Output -notmatch "from\s+(.+?)\\Lib\\site-packages\\pip") {
        return $null
    }

    $pythonPath = Join-Path $Matches[1] "python.exe"
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        return $null
    }

    $pythonResult = Invoke-CmdLine "`"$pythonPath`" --version"
    if ($pythonResult.ExitCode -ne 0) {
        return $null
    }

    return @{
        Path = $pythonPath
        Version = $pythonResult.Output
        PipVersion = $result.Output
    }
}

Write-Host "DocuRAG local development environment check"
Write-Host ""

$pythonWhereOk = Invoke-DiagnosticLine "where python" "where python"
$pyWhereOk = Invoke-DiagnosticLine "where py" "where py"

$pythonOk = Invoke-DiagnosticLine "python --version" "python --version"
$pyOk = Invoke-DiagnosticLine "py --version" "py --version"
Invoke-DiagnosticLine "py -0p" "py -0p" | Out-Null

if ($pyOk) {
    Write-Result "usable Python" $true "py launcher is available"
    Invoke-CheckLine "pip via py" "py -m pip --version" | Out-Null
}
elseif ($pythonOk) {
    Write-Result "usable Python" $true "python command is available"
    Invoke-CheckLine "pip via python" "python -m pip --version" | Out-Null
}
else {
    $pipPython = Find-PythonFromPip
    if ($null -ne $pipPython) {
        Write-Result "usable Python via pip.exe" $true ($pipPython.Version + " at " + $pipPython.Path)
        Write-Result "pip" $true $pipPython.PipVersion
    }
    else {
        Write-Result "pip" $false "Python is not available"
    }
}

Invoke-CheckLine "node --version" "node --version" | Out-Null
Invoke-CheckLine "npm.cmd --version" "npm.cmd --version" | Out-Null

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
    Write-Host "Environment check failed with $failed issue(s) and $warnings warning(s). See docs/LOCAL_DEV_SETUP.md for fixes."
    exit 1
}

Write-Host "Environment check passed with $warnings warning(s)."
exit 0
