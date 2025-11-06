@echo off
REM Telegram Forwarder Bot - Setup Script for Windows
REM This script automates the initial setup process

echo ====================================
echo Telegram Forwarder Bot - Setup
echo ====================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv is not installed!
    echo.
    echo Please install uv first:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    pause
    exit /b 1
)

echo [OK] uv is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
uv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment created
echo.

REM Install dependencies
echo Installing dependencies...
.venv\Scripts\activate && uv pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created
    echo.
    echo [IMPORTANT] Edit the .env file with your credentials!
    echo.
    echo You need to:
    echo   1. Get API credentials from https://my.telegram.org
    echo   2. Edit .env and fill in:
    echo      - API_ID
    echo      - API_HASH
    echo      - PHONE_NUMBER
    echo      - CONTACT_A
    echo      - CONTACT_B
    echo.
    echo Run: notepad .env
) else (
    echo [INFO] .env file already exists, skipping...
)

echo.
echo ====================================
echo Setup complete!
echo ====================================
echo.
echo Next steps:
echo   1. Edit .env file: notepad .env
echo   2. Activate venv: .venv\Scripts\activate
echo   3. Run the bot: python bot.py
echo.
pause
