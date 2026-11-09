@echo off
setlocal
cd /d "%~dp0"
title CDM Installer
echo ==============================
echo   CDM - Download Manager Setup
echo ==============================
echo.

if not exist "cdm.py" (
    echo [ERROR] cdm.py was not found next to this file.
    echo Put install_cdm.bat, cdm.py and cdmlogo.png in the same folder.
    pause
    exit /b 1
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
    echo A compatible Python was not found. Installing Python 3.12 with winget...
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYCMD="%LocalAppData%\Programs\Python\Python312\python.exe""
)

if not defined PYCMD (
    echo.
    echo [ERROR] Could not find or install Python automatically.
    echo Install Python 3.12 from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^)
    echo then run this file again.
    pause
    exit /b 1
)
echo Using: %PYCMD%
echo.

if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYCMD% -m venv venv
    if errorlevel 1 ( echo [ERROR] venv creation failed. & pause & exit /b 1 )
)

echo Installing requirements, please wait...
"venv\Scripts\python.exe" -m pip install --upgrade pip
"venv\Scripts\python.exe" -m pip install PyQt6 requests
if errorlevel 1 (
    echo.
    echo [ERROR] Package installation failed. Check your internet connection / antivirus and try again.
    pause
    exit /b 1
)

echo Creating launcher and shortcut...
(
echo @echo off
echo cd /d "%%~dp0"
echo start "" "%%~dp0venv\Scripts\pythonw.exe" "%%~dp0cdm.py"
) > run_cdm.bat

if exist "cdmlogo.png" (
    "venv\Scripts\python.exe" -c "from PyQt6.QtGui import QImage; from PyQt6.QtCore import Qt; QImage('cdmlogo.png').scaled(256,256,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation).save('cdm.ico')" >nul 2>&1
)
set "ICON=%~dp0cdm.ico"
if not exist "%ICON%" set "ICON=%SystemRoot%\System32\shell32.dll,175"
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\CDM.lnk'); $s.TargetPath='%~dp0venv\Scripts\pythonw.exe'; $s.Arguments='\"%~dp0cdm.py\"'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%ICON%'; $s.Save()" >nul 2>&1

echo.
echo Done! Starting CDM...
call run_cdm.bat
timeout /t 3 >nul
exit /b 0
