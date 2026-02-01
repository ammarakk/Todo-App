@echo off
REM Phase IV Kubernetes Status Script for Windows
REM Shows the status of all resources

setlocal

echo =========================================
echo Phase IV - Kubernetes Status
echo =========================================

REM Check if kubectl is available
where kubectl >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: kubectl not found.
    pause
    exit /b 1
)

echo.
echo Namespace: todo-app
echo.
echo Pods:
kubectl get pods -n todo-app -o wide

echo.
echo Services:
kubectl get svc -n todo-app

echo.
echo Deployments:
kubectl get deployments -n todo-app

echo.
echo PVCs:
kubectl get pvc -n todo-app

echo.
echo =========================================
echo To view logs:
echo   kubectl logs -n todo-app deployment/backend
echo   kubectl logs -n todo-app deployment/chatbot
echo   kubectl logs -n todo-app deployment/frontend
echo   kubectl logs -n todo-app deployment/ollama
echo =========================================

pause
