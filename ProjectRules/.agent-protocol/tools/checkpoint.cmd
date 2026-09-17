@echo off
setlocal DisableDelayedExpansion
where.exe pwsh.exe >nul 2>nul
if not errorlevel 1 (
  pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0checkpoint.ps1" %*
  if errorlevel 1 exit /b 1
  exit /b 0
)
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0checkpoint.ps1" %*
exit /b %ERRORLEVEL%
