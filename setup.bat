@echo off
setlocal enabledelayedexpansion

:: Check, if the Script is running as Administrator
net session >nul 2>&1
if errorlevel 1 (
    echo This Script has to be run as Administrator
    echo Please confirm the UAC-Request.
    powershell -Command "Start-Process -Verb runAs -FilePath '%~f0'"
    exit /b
)

REM === 1. Check if Python 3.10.0 already exists ===
set "PYTHON_CMD="

REM trying py -3.10
py -3.10 --version >nul 2>&1 && set "PYTHON_CMD=py -3.10"

REM If not found, try python3.10 in PATH
if not defined PYTHON_CMD (
    where python3.10 >nul 2>&1 && set "PYTHON_CMD=python3.10"
)

REM If nothing found check the typical installation paths
if not defined PYTHON_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    ) else if exist "C:\Program Files\Python310\python.exe" (
        set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    ) else if exist "C:\Program Files (x86)\Python310\python.exe" (
        set "PYTHON_CMD=C:\Program Files (x86)\Python310\python.exe"
    )
)

REM If not installed → Download and install Python 3.10.0
if not defined PYTHON_CMD (
    echo Python 3.10.0 not found. Downloading installer...
    powershell -NoProfile -Command ^
        "Invoke-WebRequest 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile 'python310.exe'"
    if not exist python310.exe (
        echo Error: Python-Installer could not be loaded.
        exit /b 1
    )
    echo Start Python 3.10.0-Installation...
    start /wait python310.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python310.exe

    REM Afterinstall check and set PYTHON_CMD right
    py -3.10 --version >nul 2>&1
    if not errorlevel 1 (
    	set "PYTHON_CMD=py -3.10"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    	set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    ) else if exist "C:\Program Files\Python310\python.exe" (
    	set "PYTHON_CMD=C:\Program Files\Python310\python.exe"
    ) else (
    	echo Error: Python 3.10 was installed, but not found.
    	exit /b 1
    )
)

echo Using Interpreter: %PYTHON_CMD%

REM === 2. Installing uv and dependencies ===
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install uv
%PYTHON_CMD% -m uv pip install -r extra-req.txt
%PYTHON_CMD% -m uv pip install -r requirements.txt

REM === 3. Check if 7-Zip else install ===
set "SEVENZIP_PATH=C:\Program Files\7-Zip\7z.exe"

if not exist "%SEVENZIP_PATH%" (
    echo 7-Zip not found. Downloading Installer...
    powershell -NoProfile -Command ^
        "Invoke-WebRequest 'https://www.7-zip.org/a/7z2408-x64.exe' -OutFile '7zip_installer.exe'"
    if not exist 7zip_installer.exe (
        echo Error: 7-Zip-Installer could not be downloaded.
        exit /b 1
    )
    echo Starting 7-Zip-Installation...
    start /wait 7zip_installer.exe /S
    del 7zip_installer.exe

    REM Wait for Installation to complete
    timeout /t 10 /nobreak >nul
) else (
    echo 7-Zip already installed.
)

REM === 4. Set and check 7-Zip path ===
set "SEVENZIP_PATH=C:\Program Files\7-Zip\7z.exe"
if not exist "%SEVENZIP_PATH%" (
    echo Error: 7-Zip was not found in %SEVENZIP_PATH%.
    echo Please install 7-Zip manually and restart this Install script.
    exit /b 1
)
echo 7-Zip found in: %SEVENZIP_PATH%

REM === 5. Download GPT-SoVITS Windows-Package ===
set "HF_URL=https://huggingface.co/lj1995/GPT-SoVITS-windows-package/resolve/main/GPT-SoVITS-v3lora-20250228.7z?download=true"
echo Downloading GPT-SoVITS Full-Package (ca. 6.75 GB)...
powershell -NoProfile -Command ^
    "Invoke-WebRequest '%HF_URL%' -OutFile 'GPT-SoVITS-v3lora.7z'"
if not exist GPT-SoVITS-v3lora.7z (
    echo Fehler: GPT-SoVITS-Paket could not be downloaded.
    exit /b 1
)

REM === 6. Extract GPT-SoVITS ===
echo Extracting GPT-SoVITS...
"%SEVENZIP_PATH%" x GPT-SoVITS-v3lora.7z -oGPT-SoVITS -y
if %errorlevel% neq 0 (
    echo Extraction failed. Canceling.
    exit /b 1
)

REM === 6b. Get GPT-SoVITS path ===
for /d %%i in ("GPT-SoVITS\*") do set "SOVITS_SUBDIR=%%i"
echo GPT-SoVITS path found: %SOVITS_SUBDIR%

REM === 7. Installing GPT-SoVITS dependencies ===
echo Installing GPT-SoVITS dependencies...
pushd "%SOVITS_SUBDIR%"
%PYTHON_CMD% -m uv pip install -r requirements.txt
popd

REM === 8. creating go-api.bat in GPT-SoVITS path ===
(
echo runtime\python.exe api_v2.py
echo pause
) > "%SOVITS_SUBDIR%\go-api.bat"

echo Created file go-api.bat in %SOVITS_SUBDIR%.

REM === 9. Delete GPT-SoVITS Archive ===
del GPT-SoVITS-v3lora.7z

echo Setup finished! You can now setup your Riko in the character_config.yaml. 
echo If setup finished you can run start_riko.bat
pause
