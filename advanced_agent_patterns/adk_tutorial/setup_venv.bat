@echo off
REM ADK Agent Virtual Environment Setup Script for Windows

setlocal enabledelayedexpansion

REM --- Part 1: Get your Google AI Studio API key ---
echo --- Google AI Studio API Key ---
echo Get a free key at https://aistudio.google.com/app/apikey (it starts with 'AIza...').

set /p user_api_key="Please paste your Google AI Studio API key: "

if not defined user_api_key (
    echo Error: No API key was entered.
    exit /b 1
)
echo API key received.

echo Setting up ADK Agent virtual environment...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is required but not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo Python %python_version% detected

REM Create virtual environment
echo Creating virtual environment...
python -m venv .adk_env

REM Activate virtual environment
echo Activating virtual environment...
call .adk_env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM --- Create .env file (Google AI Studio API key path) ---
echo Creating .env file...
(
    echo # Environment variables for ADK Agent, created by setup_venv.bat
    echo GOOGLE_GENAI_USE_VERTEXAI=FALSE
    echo GOOGLE_API_KEY=!user_api_key!
) > .env

echo Setup complete! A '.env' file has been created with your Google AI Studio API key.
echo.
echo To activate the virtual environment, run:
echo    .adk_env\Scripts\activate
echo.
echo Your agent will automatically load the settings from the .env file.
echo To deactivate the virtual environment, run:
echo    deactivate
echo.
echo Press any key to continue...
pause >nul
