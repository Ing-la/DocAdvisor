@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe scripts\main.py
) else (
    python scripts\main.py
)
pause



