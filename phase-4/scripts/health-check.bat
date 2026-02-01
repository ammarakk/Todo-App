@echo off
REM Phase IV Health Check Script for Windows
REM Checks the health of all services

setlocal enabledelayedexpansion

echo =========================================
echo Phase IV - Health Check
echo =========================================
echo.

REM Check Docker
docker info >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Docker: Running
    echo.
    echo Docker Containers:
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr /C:"NAMES" /C:"todo"
) else (
    echo - Docker: Not running
)

echo.
echo ----------------------------------------
echo.

REM Check Kubernetes
kubectl cluster-info >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Kubernetes: Connected
    echo.
    echo Pods in todo-app namespace:
    kubectl get pods -n todo-app -o wide 2>nul
    if !ERRORLEVEL! neq 0 echo No pods found or namespace not created
) else (
    echo - Kubernetes: Not connected
)

echo.
echo ----------------------------------------
echo.

REM Check local services
echo Local Service Health Checks:
echo.

REM Backend health
curl -s http://localhost:8000/api/health >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Backend (localhost:8000): Healthy
) else (
    echo - Backend (localhost:8000): Unreachable
)

REM Chatbot health
curl -s http://localhost:8001/api/health >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Chatbot (localhost:8001): Healthy
) else (
    echo - Chatbot (localhost:8001): Unreachable
)

REM Frontend health
curl -s http://localhost:3000 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Frontend (localhost:3000): Healthy
) else (
    echo - Frontend (localhost:3000): Unreachable
)

REM Ollama health
curl -s http://localhost:11434 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo + Ollama (localhost:11434): Healthy
) else (
    echo - Ollama (localhost:11434): Unreachable
)

echo.
echo =========================================
echo Health Check Complete!
echo =========================================

pause
