@echo off
cd /d "%~dp0"
if not exist venv (
    echo Virtual environment not found. Please create it first.
    pause
    exit /b
)
start "" "venv\Scripts\pythonw.exe" main.py
echo Application started in background. Check the system tray.
