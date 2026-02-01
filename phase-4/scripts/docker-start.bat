@echo off
REM Phase IV Docker Start Script for Windows
REM Starts all services using Docker Compose

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set COMPOSE_FILE=%PROJECT_ROOT%\infra\docker\docker-compose.yml

echo =========================================
echo Phase IV - Starting Docker Services
echo =========================================

cd /d "%PROJECT_ROOT%\infra\docker"

echo.
echo Starting services...
docker-compose -f "%COMPOSE_FILE%" up -d

echo.
echo Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo Service Status:
docker-compose -f "%COMPOSE_FILE%" ps

echo.
echo =========================================
echo Services Started!
echo.
echo Access URLs:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   Chatbot:   http://localhost:8001
echo   Ollama:    http://localhost:11434
echo.
echo View logs: docker-compose -f %COMPOSE_FILE% logs -f
echo Stop: docker-compose -f %COMPOSE_FILE% down
echo =========================================

pause
