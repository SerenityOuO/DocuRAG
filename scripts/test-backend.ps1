Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"
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

$pythonCommand = $null
$pythonArgs = @()

if ((Get-Command py -ErrorAction SilentlyContinue) -and (Test-NativeCommand "py" @("-3", "--version"))) {
    $pythonCommand = "py"
    $pythonArgs = @("-3")
}
elseif ((Get-Command python -ErrorAction SilentlyContinue) -and (Test-NativeCommand "python" @("--version"))) {
    $pythonCommand = "python"
}

if ($null -eq $pythonCommand) {
    Write-Error "No usable Python found. Run scripts/check-dev-env.ps1 and see docs/LOCAL_DEV_SETUP.md."
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "Creating backend virtual environment at $venvRoot"
    & $pythonCommand @pythonArgs -m venv $venvRoot
}

Push-Location $backendRoot
try {
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -e ".[dev]"
    & $venvPython -m pytest
}
finally {
    Pop-Location
}
