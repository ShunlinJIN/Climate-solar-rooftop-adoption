param(
    [string]$PythonPath = "",
    [string]$RscriptPath = "",
    [string]$OutputDir = "",
    [switch]$Install
)
$ErrorActionPreference = "Stop"
if ($PythonPath) {
    $PythonCommand = $PythonPath; $PythonPrefix = @()
} elseif (Test-Path (Join-Path $PSScriptRoot ".venv/Scripts/python.exe")) {
    $PythonCommand = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"; $PythonPrefix = @()
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = (Get-Command py).Source; $PythonPrefix = @("-3")
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = (Get-Command python).Source; $PythonPrefix = @()
} else {
    throw "Python was not found. Install Python 3.10 or newer, or pass -PythonPath with the full path to python.exe."
}
& $PythonCommand @PythonPrefix -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10 or newer is required'; print('Python:', sys.executable)"
if ($LASTEXITCODE -ne 0) { throw "The selected Python interpreter could not be started." }
if ($RscriptPath) { $env:RSCRIPT = $RscriptPath }
$RExe = & $PythonCommand @PythonPrefix (Join-Path $PSScriptRoot "code/find_rscript.py")
if ($LASTEXITCODE -ne 0 -or -not $RExe) { throw "Rscript was not found. Pass -RscriptPath with the full path to Rscript.exe." }
$env:RSCRIPT = ($RExe | Select-Object -Last 1).Trim()
Write-Host "Rscript: $env:RSCRIPT"
if ($Install) {
    & $PythonCommand @PythonPrefix -m ensurepip --upgrade
    if ($LASTEXITCODE -ne 0) { throw "Could not initialize pip in the selected Python environment." }
    & $PythonCommand @PythonPrefix -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { throw "Python dependency installation failed." }
    & $env:RSCRIPT --vanilla (Join-Path $PSScriptRoot "code/setup.R")
    if ($LASTEXITCODE -ne 0) { throw "R dependency installation failed." }
}
$RunArgs = @((Join-Path $PSScriptRoot "code/run_public.py"))
if ($OutputDir) { $RunArgs += @("--output-dir", $OutputDir) }
& $PythonCommand @PythonPrefix @RunArgs
if ($LASTEXITCODE -ne 0) { throw "Public reproduction failed. Read the error and the output/log directory." }
