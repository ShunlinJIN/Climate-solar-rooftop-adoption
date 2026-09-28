param([string]$RscriptPath = "")
$ErrorActionPreference = "Stop"
if ($RscriptPath) { $env:RSCRIPT = $RscriptPath }
python (Join-Path $PSScriptRoot "code/run_public.py")
if ($LASTEXITCODE -ne 0) { throw "Public reproduction failed." }
