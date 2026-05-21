param(
    [switch]$CheckPaddleOcr,
    [string]$PaddleOcrSamplePath = ""
)

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
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
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

function Get-PythonCommandLine {
    $supportedPyLaunchers = @("py -3.12", "py -3.11")
    foreach ($candidate in $supportedPyLaunchers) {
        $candidateCheck = Invoke-CmdLine "$candidate --version"
        if ($candidateCheck.ExitCode -eq 0) {
            return $candidate
        }
    }

    $pyCheck = Invoke-CmdLine "py -3 --version"
    if ($pyCheck.ExitCode -eq 0) {
        return "py -3"
    }

    $pythonCheck = Invoke-CmdLine "python --version"
    if ($pythonCheck.ExitCode -eq 0) {
        return "python"
    }

    $pipPython = Find-PythonFromPip
    if ($null -ne $pipPython) {
        return "`"$($pipPython.Path)`""
    }

    return $null
}

function Invoke-PaddleOcrBaseline {
    param([string]$SamplePath)

    $repoRoot = Split-Path -Parent $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($SamplePath)) {
        $SamplePath = Join-Path $repoRoot "sample-data/documents/sample-ocr-invoice.png"
    }

    if (-not (Test-Path -LiteralPath $SamplePath)) {
        Write-Result "PaddleOCR sample image" $false "sample image not found: $SamplePath"
        return $false
    }

    $resolvedSamplePath = (Resolve-Path -LiteralPath $SamplePath).Path
    Write-Host ""
    Write-Host "PaddleOCR baseline check"
    Write-Host "Sample image: $resolvedSamplePath"

    $pythonCommand = Get-PythonCommandLine
    if ([string]::IsNullOrWhiteSpace($pythonCommand)) {
        Write-Result "PaddleOCR Python runner" $false "No usable Python command found for PaddleOCR baseline."
        return $false
    }

    Write-Result "PaddleOCR Python runner" $true $pythonCommand

    $baselineScript = @'
import importlib
import json
import os
from pathlib import Path
import sys
import traceback

sample_path = Path(sys.argv[1])
failed = False
engine = None
PaddleOCR = None

def print_stage(status, name, detail):
    print(f"[{status}] {name} - {detail}")

print_stage("INFO", "python", f"{sys.version.split()[0]} at {sys.executable}")
if sys.version_info >= (3, 13):
    print_stage("WARN", "python support", "PaddleOCR real OCR path in this project supports Python 3.11 or 3.12; use Python 3.12 for backend[real-ocr]")
else:
    print_stage("PASS", "python support", "Python version is within the project PaddleOCR support window")

try:
    paddle = importlib.import_module("paddle")
    paddleocr_module = importlib.import_module("paddleocr")
    PaddleOCR = getattr(paddleocr_module, "PaddleOCR")
    print_stage(
        "PASS",
        "dependency import",
        f"paddle={getattr(paddle, '__version__', 'unknown')}; paddleocr={getattr(paddleocr_module, '__version__', 'unknown')}",
    )
except Exception as exc:
    failed = True
    print_stage("FAIL", "dependency import", f"{type(exc).__name__}: {exc}")
    traceback.print_exc()

model_root = Path(os.environ.get("PADDLEOCR_HOME", Path.home() / ".paddleocr")).expanduser()
try:
    if model_root.exists():
        entries = sorted(path.name for path in model_root.iterdir())
        preview = ", ".join(entries[:5]) if entries else "(empty)"
        print_stage("PASS", "model cache state", f"{model_root} exists; entries: {preview}")
    else:
        print_stage("WARN", "model cache state", f"{model_root} does not exist; initialization may need model download")
except Exception as exc:
    print_stage("WARN", "model cache state", f"{type(exc).__name__}: {exc}")

if PaddleOCR is not None:
    try:
        engine = PaddleOCR(use_angle_cls=True, lang="en")
        print_stage("PASS", "engine initialization", "PaddleOCR engine initialized")
    except Exception as exc:
        failed = True
        print_stage("FAIL", "engine initialization or model download", f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
else:
    print_stage("SKIP", "engine initialization", "dependency import failed")

if engine is not None:
    try:
        try:
            raw_result = engine.ocr(str(sample_path), cls=True)
        except TypeError:
            raw_result = engine.ocr(str(sample_path))

        line_count = 0
        text_preview = []
        for page in raw_result or []:
            items = page
            if (
                isinstance(page, (list, tuple))
                and len(page) >= 2
                and isinstance(page[1], (list, tuple))
                and page[1]
                and isinstance(page[1][0], str)
            ):
                items = [page]

            for item in items or []:
                if (
                    isinstance(item, (list, tuple))
                    and len(item) >= 2
                    and isinstance(item[1], (list, tuple))
                    and item[1]
                ):
                    text = str(item[1][0]).strip()
                    if text:
                        line_count += 1
                        if len(text_preview) < 3:
                            text_preview.append(text)

        print_stage(
            "PASS" if line_count else "FAIL",
            "sample image OCR runtime",
            f"recognized_lines={line_count}; preview={json.dumps(text_preview, ensure_ascii=False)}",
        )
        if not line_count:
            failed = True
    except Exception as exc:
        failed = True
        print_stage("FAIL", "sample image OCR runtime", f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
else:
    print_stage("SKIP", "sample image OCR runtime", "engine initialization failed")

sys.exit(1 if failed else 0)
'@

    $tempScript = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), ".py")
    try {
        Set-Content -LiteralPath $tempScript -Value $baselineScript -Encoding UTF8
        $result = Invoke-CmdLine "$pythonCommand `"$tempScript`" `"$resolvedSamplePath`""
        if (-not [string]::IsNullOrWhiteSpace($result.Output)) {
            Write-Host $result.Output
        }

        if ($result.ExitCode -eq 0) {
            Write-Result "PaddleOCR baseline" $true "dependency import, engine initialization, and sample image OCR completed"
            return $true
        }

        Write-Result "PaddleOCR baseline" $false "exit code $($result.ExitCode); see stage output above"
        return $false
    }
    finally {
        if (Test-Path -LiteralPath $tempScript) {
            Remove-Item -LiteralPath $tempScript -Force
        }
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

if ($CheckPaddleOcr) {
    Invoke-PaddleOcrBaseline $PaddleOcrSamplePath | Out-Null
}

Write-Host ""
if ($failed -gt 0) {
    Write-Host "Environment check failed with $failed issue(s) and $warnings warning(s). See docs/LOCAL_DEV_SETUP.md for fixes."
    exit 1
}

Write-Host "Environment check passed with $warnings warning(s)."
exit 0
