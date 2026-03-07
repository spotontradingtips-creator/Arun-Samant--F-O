@echo off
TITLE SENTINEL CONTROL CENTER - MOBILE SYNC
COLOR 0B
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
echo.
echo  ================================================
echo   SENTINEL HUB v2.0 - TELEGRAM CONTROL CENTER
echo  ================================================
echo.
echo  [SYSTEM] Initializing Telegram Listener...
echo  [SYSTEM] Remote Access: ENABLED
echo.

cd /d "%~dp0"
python src/telegram_bot.py
pause
