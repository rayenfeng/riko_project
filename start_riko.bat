@echo off
setlocal enabledelayedexpansion

REM === 1. Setting Python 3.10 Interpreter ===
set "PYTHON_CMD=py -3.10"
%PYTHON_CMD% --version >nul 2>&1 || (
    echo Python 3.10 not found, Please install Python 3.10 or run install.bat first!
    pause
    exit /b 1
)

REM === 2. Finding GPT-SoVITS path ===
set "SOVITS_SUBDIR="
for /d %%i in ("GPT-SoVITS\*") do (
    set "SOVITS_SUBDIR=%%i"
)

if "%SOVITS_SUBDIR%"=="" (
    echo GPT-SoVITS path not found.
    pause
    exit /b 1
)

echo Found GPT-SoVITS Path: %SOVITS_SUBDIR%

REM === 3. Starting GPT-SoVITS API ===
pushd "%SOVITS_SUBDIR%"
echo Starting go-api.bat...
start "" go-api.bat
popd

REM === 4. Starting Riko ===
echo Starting Riko...
%PYTHON_CMD% server\main_chat.py

pause
