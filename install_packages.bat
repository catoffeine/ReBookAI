@echo off
setlocal enabledelayedexpansion

if "%VIRTUAL_ENV%"=="" (
    echo Error: No virtual environment is currently active.
    echo Please activate your virtual environment and try again.
    pause
    exit /b 1
)

echo Virtual environment detected at: %VIRTUAL_ENV%

if not exist "requirements.txt" (
    echo Error: 'requirements.txt' file not found in the current directory.
    echo Please ensure the file exists and try again.
    pause
    exit /b 1
)

echo Found 'requirements.txt'. Installing packages...

echo Running: pip install -r requirements.txt
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install packages from 'requirements.txt'.
    echo Please check the error messages above and resolve any issues.
    pause
    exit /b 1
)

echo Successfully installed all packages from 'requirements.txt'.
exit /b 0