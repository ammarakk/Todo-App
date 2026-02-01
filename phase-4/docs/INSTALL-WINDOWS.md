# Phase IV - Windows Installation Guide

## Prerequisites for Kubernetes and Helm on Windows

This guide will help you install Kubernetes (kubectl) and Helm on Windows for Phase IV deployment.

---

## 1. Install Kubernetes CLI (kubectl)

### Option A: Using Chocolatey (Recommended)
```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install kubectl
choco install kubernetes-cli -y
```

### Option B: Manual Download
1. Download the latest kubectl binary from:
   https://kubernetes.io/docs/tasks/tools/#kubectl

2. Move the downloaded file to a directory in your PATH, e.g.:
   ```
   C:\kubectl\kubectl.exe
   ```

3. Add to PATH:
   - Press Win + R, type `sysdm.cpl`
   - Go to Advanced → Environment Variables
   - Edit PATH and add `C:\kubectl\`

4. Verify installation:
```powershell
kubectl version --client
```

---

## 2. Install Kubernetes Cluster (Choose One)

### Option A: Docker Desktop (Easiest)
1. Install Docker Desktop for Windows from:
   https://www.docker.com/products/docker-desktop/

2. Enable Kubernetes in Docker Desktop:
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"

3. Verify:
```powershell
kubectl cluster-info
```

### Option B: Minikube
```powershell
# Install using Chocolatey
choco install minikube -y

# Start Minikube
minikube start

# Verify
kubectl get nodes
```

### Option C: Kind (Kubernetes in Docker)
```powershell
# Install using Chocolatey
choco install kind -y

# Create cluster
kind create cluster --name todo-app

# Verify
kubectl get nodes
```

---

## 3. Install Helm

### Using Chocolatey (Recommended)
```powershell
choco install kubernetes-helm -y
```

### Manual Installation
1. Download from: https://github.com/helm/helm/releases

2. Rename to `helm.exe` and add to PATH

3. Verify:
```powershell
helm version
```

---

## 4. Verify Installation

Run this command to verify everything is set up:

```powershell
# Check kubectl
kubectl version --client

# Check cluster
kubectl cluster-info

# Check helm
helm version

# List nodes
kubectl get nodes
```

---

## 5. Next Steps

Once installed, you can deploy Phase IV:

### Using Kubernetes (kubectl):
```powershell
cd phase-4/infra/k8s
kubectl apply -f namespace.yaml
kubectl apply -f 00-postgres.yaml
kubectl apply -f 01-ollama.yaml
kubectl apply -f 02-backend.yaml
kubectl apply -f 03-chatbot.yaml
kubectl apply -f 04-frontend.yaml
```

### Using Helm:
```powershell
cd phase-4/scripts
bash helm-deploy.sh
```

Or on Windows PowerShell:
```powershell
helm install todo-app .\infra\helm\todo-app -n todo-app --create-namespace
```

---

## Troubleshooting

### kubectl: command not found
- Ensure kubectl is in your PATH
- Restart your terminal/PowerShell after adding to PATH

### Cannot connect to cluster
- Ensure Docker Desktop Kubernetes is enabled OR
- Ensure Minikube/Kind cluster is running

### Helm: command not found
- Ensure Helm is in your PATH
- Restart PowerShell after installation

### Images not found
- Build images first using Docker Desktop:
```powershell
cd phase-4
docker build -t todo-backend:latest ./apps/todo-backend
docker build -t todo-chatbot:latest ./apps/chatbot
docker build -t todo-frontend:latest ./apps/todo-frontend
```

---

## Quick Start Script (PowerShell)

Save as `setup-windows.ps1` and run:

```powershell
# Check admin privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run as Administrator"
    exit
}

# Install Chocolatey if not exists
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

# Install tools
choco install kubernetes-cli kubernetes-helm docker-desktop -y

Write-Host "Installation complete! Please restart your shell and verify with:"
Write-Host "kubectl version --client"
Write-Host "helm version"
Write-Host "docker version"
```

Run with:
```powershell
powershell -ExecutionPolicy Bypass -File setup-windows.ps1
```
