Write-Output test4
Write-Output test4
Write-Output test4

$ErrorActionPreference = 'Continue'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8 # Set console output encoding to UTF-8

$OLDPWD = $PWD
Set-Location -Path $PSScriptRoot
Write-Host "workpath change to: $PWD"

& ./test.exe

Write-Output done

Set-Location -Path $OLDPWD
