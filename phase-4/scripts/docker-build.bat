@echo off
REM Phase IV Docker Build Script for Windows
REM Builds all Docker images for the Todo application

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo =========================================
echo Phase IV - Building Docker Images
echo =========================================

cd /d "%PROJECT_ROOT%"

REM Build Backend
echo.
echo Building Backend Image...
cd apps\todo-backend
docker build -t todo-backend:latest .
cd "%PROJECT_ROOT%"

REM Build Chatbot
echo.
echo Building Chatbot Image...
cd apps\chatbot
docker build -t todo-chatbot:latest .
cd "%PROJECT_ROOT%"

REM Build Frontend
echo.
echo Building Frontend Image...
cd apps\todo-frontend
docker build -t todo-frontend:latest .
cd "%PROJECT_ROOT%"

echo.
echo =========================================
echo Build Complete!
echo Images:
echo   - todo-backend:latest
echo   - todo-chatbot:latest
echo   - todo-frontend:latest
echo   - ollama/ollama:latest (pulled on first run)
echo =========================================

pause
