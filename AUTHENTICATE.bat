@echo off
echo.
echo ================================================================
echo   mStock API Authentication
echo ================================================================
echo.

cd /d "%~dp0"
python src/scripts/authenticate.py

pause
