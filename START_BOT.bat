@echo off
title SENTINEL BOT - NEURAL CORE
color 0a
echo ==================================================
echo       SENTINEL F&O TRADING BOT - CORE SYSTEM
echo ==================================================
echo.
echo [1] CHECKING ENVIRONMENT...
python --version
echo.
echo [2] LAUNCHING MAIN PROCESS...
echo.
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [CRITICAL ERROR] The bot has encountered a fatal issue and stopped.
    echo Please review the error messages above for details.
    echo.
)

echo.
echo SYSTEM HALTED.
pause
