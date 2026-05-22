Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
$pytestTemp = Join-Path $repoRoot ".tmp/backend-pytest-$([guid]::NewGuid().ToString("N"))"
$venvRoot = Join-Path $backendRoot ".venv"
$venvPython = Join-Path $venvRoot "Scripts/python.exe"

function Test-NativeCommand {
    param(
        [string]$CommandName,
        [string[]]$Arguments
    )

    try {
        $output = & $CommandName @Arguments 2>&1
        return ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE)
    }
    catch {
        return $false
    }
}

function Find-PythonFromPip {
    $pipCommand = Get-Command pip -ErrorAction SilentlyContinue
    if ($null -eq $pipCommand) {
        return $null
    }

    try {
        $pipOutput = & $pipCommand.Source --version 2>&1
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            return $null
        }

        $pipText = ($pipOutput | Out-String).Trim()
        if ($pipText -notmatch "from\s+(.+?)\\Lib\\site-packages\\pip") {
            return $null
        }

        $pythonPath = Join-Path $Matches[1] "python.exe"
        if ((Test-Path -LiteralPath $pythonPath) -and (Test-NativeCommand $pythonPath @("--version"))) {
            return $pythonPath
        }
    }
    catch {
        return $null
    }

    return $null
}

function Invoke-Step {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments
    )

    Write-Host $Name
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

$pythonCommand = $null
$pythonArgs = @()

if ((Get-Command py -ErrorAction SilentlyContinue) -and (Test-NativeCommand "py" @("-3.12", "--version"))) {
    $pythonCommand = "py"
    $pythonArgs = @("-3.12")
}
elseif ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-NativeCommand "python" @("-c", "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)"))) {
    $pythonCommand = "python"
}
else {
    $pythonFromPip = Find-PythonFromPip
    if ($null -ne $pythonFromPip -and (Test-NativeCommand $pythonFromPip @("-c", "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)"))) {
        $pythonCommand = $pythonFromPip
    }
}

if ($null -eq $pythonCommand) {
    Write-Error "No usable Python 3.12 found. Run scripts/check-dev-env.ps1 and see docs/LOCAL_DEV_SETUP.md."
}

if ((Test-Path -LiteralPath $venvPython) -and (-not (Test-NativeCommand $venvPython @("-c", "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)")))) {
    Write-Error "Existing backend virtual environment is not Python 3.12. Remove backend/.venv and rerun this script."
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating backend virtual environment at $venvRoot"
    Invoke-Step "Create backend virtual environment" $pythonCommand ($pythonArgs + @("-m", "venv", $venvRoot))
}

Push-Location $backendRoot
try {
    Invoke-Step "Check pip" $venvPython @("-m", "pip", "--version")
    Invoke-Step "Install backend build dependencies" $venvPython @("-m", "pip", "--disable-pip-version-check", "install", "setuptools>=68")
    Invoke-Step "Install backend dev dependencies" $venvPython @("-m", "pip", "--disable-pip-version-check", "install", "--no-build-isolation", "-e", ".[dev]")
    Invoke-Step "Run pytest" $venvPython @("-m", "pytest", "--basetemp", $pytestTemp)
}
finally {
    Pop-Location
}
