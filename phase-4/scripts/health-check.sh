#!/bin/bash
# Phase IV Health Check Script
# Checks the health of all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Phase IV - Health Check"
echo "========================================="
echo ""

# Check Docker
if docker info &> /dev/null; then
    echo "✓ Docker: Running"
    echo ""
    echo "Docker Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAME|todo"
else
    echo "✗ Docker: Not running"
fi

echo ""
echo "----------------------------------------"
echo ""

# Check Kubernetes
if kubectl cluster-info &> /dev/null; then
    echo "✓ Kubernetes: Connected"
    echo ""
    echo "Pods in todo-app namespace:"
    kubectl get pods -n todo-app -o wide || echo "No pods found"
else
    echo "✗ Kubernetes: Not connected"
fi

echo ""
echo "----------------------------------------"
echo ""

# Check local services
echo "Local Service Health Checks:"
echo ""

# Backend health
if curl -s http://localhost:8000/api/health &> /dev/null; then
    echo "✓ Backend (localhost:8000): Healthy"
else
    echo "✗ Backend (localhost:8000): Unreachable"
fi

# Chatbot health
if curl -s http://localhost:8001/api/health &> /dev/null; then
    echo "✓ Chatbot (localhost:8001): Healthy"
else
    echo "✗ Chatbot (localhost:8001): Unreachable"
fi

# Frontend health
if curl -s http://localhost:3000 &> /dev/null; then
    echo "✓ Frontend (localhost:3000): Healthy"
else
    echo "✗ Frontend (localhost:3000): Unreachable"
fi

# Ollama health
if curl -s http://localhost:11434 &> /dev/null; then
    echo "✓ Ollama (localhost:11434): Healthy"
else
    echo "✗ Ollama (localhost:11434): Unreachable"
fi

echo ""
echo "========================================="
echo "Health Check Complete!"
echo "========================================="
