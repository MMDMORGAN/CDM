@echo off
setlocal
cd /d "%~dp0"
set "SRC=%~dp0"
title CDM - Build single EXE
echo ==========================================
echo   CDM - building one standalone CDM.exe
echo ==========================================
echo.

for %%F in (cdm.py cdmlogo.png cdmlogo_1.png Irancell_Duran-Medium.ttf) do (
    if not exist "%SRC%%%F" (
        echo [ERROR] Missing file: %%F  ^(keep it next to this .bat^)
        pause
        exit /b 1
    )
)

set "PYCMD="
for %%V in (3.13 3.12 3.11 3.10) do (
    if not defined PYCMD (
        py -%%V -c "import sys" >nul 2>&1 && set "PYCMD=py -%%V"
    )
)
if not defined PYCMD (
    python -c "import sys;sys.exit(0 if (3,9)<=sys.version_info[:2]<=(3,13) else 1)" >nul 2>&1 && set "PYCMD=python"
)
if not defined PYCMD (
    echo Python not found. Installing Python 3.12 with winget...
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYCMD="%LocalAppData%\Programs\Python\Python312\python.exe""
)
if not defined PYCMD (
    echo [ERROR] Python 3.10-3.13 is required: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Using: %PYCMD%

set "WORK=%TEMP%\cdm_build_%RANDOM%"
mkdir "%WORK%" || ( echo [ERROR] Cannot create temp folder & pause & exit /b 1 )
copy /y "%SRC%cdm.py" "%WORK%\" >nul
copy /y "%SRC%cdmlogo.png" "%WORK%\" >nul
copy /y "%SRC%cdmlogo_1.png" "%WORK%\" >nul
copy /y "%SRC%Irancell_Duran-Medium.ttf" "%WORK%\" >nul
cd /d "%WORK%"

echo.
echo [1/4] Creating temporary environment...
%PYCMD% -m venv venv
if errorlevel 1 goto :fail
echo [2/4] Installing build tools ^(internet required, a few minutes^)...
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check --upgrade pip
"venv\Scripts\python.exe" -m pip install --disable-pip-version-check PyQt6 requests pyinstaller pillow cryptography
if errorlevel 1 goto :fail

echo [3/4] Building CDM.exe ...
"venv\Scripts\python.exe" -c "from PIL import Image; Image.open('cdmlogo.png').convert('RGBA').save('cdm.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
"venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name CDM --icon cdm.ico ^
    --add-data "cdmlogo.png;." --add-data "cdmlogo_1.png;." --add-data "Irancell_Duran-Medium.ttf;." ^
    --exclude-module tkinter cdm.py
if not exist "dist\CDM.exe" goto :fail

echo [4/4] Finishing...
copy /y "dist\CDM.exe" "%SRC%CDM.exe" >nul
cd /d "%SRC%"
rmdir /s /q "%WORK%"
echo.
echo Done!  CDM.exe is ready next to this file.
echo You can now delete everything else - the logo and font are inside the exe.
start "" "%SRC%CDM.exe"
timeout /t 4 >nul
exit /b 0

:fail
echo.
echo [ERROR] Build failed. Check internet connection / antivirus and try again.
cd /d "%SRC%"
pause
exit /b 1
