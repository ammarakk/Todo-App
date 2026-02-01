@echo off
REM Phase IV Docker Stop Script for Windows
REM Stops all Docker services

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set COMPOSE_FILE=%PROJECT_ROOT%\infra\docker\docker-compose.yml

echo =========================================
echo Phase IV - Stopping Docker Services
echo =========================================

cd /d "%PROJECT_ROOT%\infra\docker"

echo.
echo Stopping services...
docker-compose -f "%COMPOSE_FILE%" down

echo.
echo =========================================
echo Services Stopped!
echo.
echo To start again: scripts\docker-start.bat
echo =========================================

pause
