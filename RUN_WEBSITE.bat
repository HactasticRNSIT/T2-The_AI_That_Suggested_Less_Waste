@echo off
cd /d "%~dp0"
echo Starting EcoWise at http://127.0.0.1:5000/
echo Keep this window open while using the website.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve_static_5000.ps1"
pause
