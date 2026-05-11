param(
    [string]$ApiBaseUrl = "https://kingsley-api-ezfneafjdvbyeedx.westeurope-01.azurewebsites.net/api",
    [int]$Timeout = 20,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"
$validationScript = Join-Path $repoRoot "scripts\hosted_etl_validation.py"

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe"
}

if (-not (Test-Path $validationScript)) {
    throw "Validation helper not found at $validationScript"
}

$arguments = @(
    $validationScript
    "--api-base-url"
    $ApiBaseUrl
    "--timeout"
    $Timeout
)

if ($Json) {
    $arguments += "--json"
}

& $pythonExe @arguments
