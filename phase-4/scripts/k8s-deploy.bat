@echo off
REM Phase IV Kubernetes Deploy Script for Windows
REM Deploys the application to Kubernetes using kubectl

setlocal

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set K8S_DIR=%PROJECT_ROOT%\infra\k8s

echo =========================================
echo Phase IV - Deploying to Kubernetes
echo =========================================

REM Check if kubectl is available
where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: kubectl not found. Please install kubectl first.
    echo See: phase-4\docs\INSTALL-WINDOWS.md
    pause
    exit /b 1
)

REM Check cluster connection
echo.
echo Checking cluster connection...
kubectl cluster-info >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Cannot connect to Kubernetes cluster.
    echo Please ensure your cluster is running and kubeconfig is configured.
    pause
    exit /b 1
)

echo Cluster connected successfully.

REM Create namespace
echo.
echo Creating namespace...
kubectl apply -f "%K8S_DIR%\namespace.yaml"

REM Deploy in order
echo.
echo Deploying PostgreSQL...
kubectl apply -f "%K8S_DIR%\00-postgres.yaml"

echo.
echo Deploying Ollama...
timeout /t 5 /nobreak >nul
kubectl apply -f "%K8S_DIR%\01-ollama.yaml"

echo.
echo Deploying Backend...
timeout /t 5 /nobreak >nul
kubectl apply -f "%K8S_DIR%\02-backend.yaml"

echo.
echo Deploying Chatbot...
timeout /t 5 /nobreak >nul
kubectl apply -f "%K8S_DIR%\03-chatbot.yaml"

echo.
echo Deploying Frontend...
timeout /t 5 /nobreak >nul
kubectl apply -f "%K8S_DIR%\04-frontend.yaml"

echo.
echo =========================================
echo Deployment Complete!
echo.
echo Services:
kubectl get svc -n todo-app
echo.
echo Pods:
kubectl get pods -n todo-app
echo.
echo =========================================
echo To access the application:
echo 1. For local development, use port-forward:
echo    kubectl port-forward -n todo-app svc/frontend-service 3000:3000
echo.
echo 2. For production, configure an Ingress controller
echo =========================================

pause
