@echo off
setlocal
cd /d "%~dp0"

title GGF CMNET2

set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"
set "CUDA_VISIBLE_DEVICES=0"

if not exist "%~dp0.venv\Scripts\python.exe" (
  echo [ERROR] Local venv not found.
  echo Run the installer first.
  pause
  exit /b 1
)

call "%~dp0.venv\Scripts\activate.bat"
"%~dp0.venv\Scripts\python.exe" "%~dp0app\app.py"
pause
