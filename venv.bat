@echo off
setlocal enabledelayedexpansion

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo Python 3 is available as 'python3'.
    python3 --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo Using python3...
        set python_cmd=python3
    ) else (
        echo Warning: python3 is detected but cannot be executed.
        echo Falling back to 'python'...
        goto check_python
    )
) else (
    echo Python 3 python3 isn't found on the PATH.
    goto check_python
)

:check_python
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Python is available as 'python'.
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo Using python...
        set python_cmd=python
    ) else (
        echo Error: Neither 'python3' nor 'python' is usable.
        echo Please ensure Python is installed and added to your PATH.
        exit /b 1
    )
) else (
    echo Error: Neither 'python3' nor 'python' is found on the PATH.
    echo Please install Python and add it to your PATH.
    exit /b 1
)

for /f "tokens=2 delims= " %%a in ('%python_cmd% --version 2^>^&1') do set python_version=%%a
for /f "tokens=1,2,3 delims=." %%i in ("%python_version%") do (
    set python_major=%%i
)
if "%python_major%" NEQ "3" (
    echo Python version is not 3.x. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

if exist "venv\" (
    echo Virtual environment "venv" already exists. Skipping creation.
) else (
    echo Virtual environment "venv" not found. Creating one...
    %python_cmd% -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        exit /b 1
    )
)

endlocal

echo Activating virtual environment...
cmd /k ".\venv\Scripts\activate.bat"