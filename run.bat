@echo off
SETLOCAL EnableDelayedExpansion

echo =====================================================================
echo    Airline Passenger Satisfaction Prediction Project Setup & Run
echo =====================================================================

:: Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

:: Virtual environment directory
set VENV_DIR=.venv

:: Create virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo [INFO] Creating Python virtual environment in %VENV_DIR%...
    python -m venv %VENV_DIR%
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate"

:: Install/Upgrade dependencies
echo [INFO] Checking and installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Run web app GUI
echo [INFO] Starting the AeroPredict GUI Dashboard...
echo [INFO] Open your web browser and navigate to http://127.0.0.1:5000/
python app.py %*
if !ERRORLEVEL! neq 0 (
    echo [ERROR] Pipeline execution failed.
    pause
    exit /b 1
)

echo [INFO] Pipeline execution completed successfully.
call deactivate
echo =====================================================================
pause
