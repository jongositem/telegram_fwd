@echo off
REM Telegram Forwarder Bot - Run Script for Windows
REM Activates virtual environment and starts the bot

echo ====================================
echo Telegram Forwarder Bot
echo ====================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup first:
    echo   setup.bat
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file with your credentials:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Run the bot
echo [INFO] Starting bot...
echo.
python bot.py

pause
