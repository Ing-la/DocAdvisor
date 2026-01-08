@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe scripts\tkinter_app.py
) else (
    python scripts\tkinter_app.py
)
pause



