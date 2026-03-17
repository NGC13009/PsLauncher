$ErrorActionPreference = 'Continue'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8 # Set console output encoding to UTF-8

$OLDPWD = $PWD
Set-Location -Path $PSScriptRoot
Write-Host "workpath change to: $PWD"

conda activate py312

python ./PsLauncher.py

Set-Location -Path $OLDPWD
