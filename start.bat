@echo off
cd /d "%~dp0"
python app.py
if errorlevel 1 (
  echo.
  echo Python/Flask did not start. Starting the no-install preview server instead.
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve_static_5000.ps1"
)
