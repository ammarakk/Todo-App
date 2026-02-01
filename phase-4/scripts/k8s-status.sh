#!/bin/bash
# Phase IV Kubernetes Status Script
# Shows the status of all resources

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Phase IV - Kubernetes Status"
echo "========================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl not found."
    exit 1
fi

echo ""
echo "Namespace: todo-app"
echo ""
echo "Pods:"
kubectl get pods -n todo-app -o wide

echo ""
echo "Services:"
kubectl get svc -n todo-app

echo ""
echo "Deployments:"
kubectl get deployments -n todo-app

echo ""
echo "PVCs:"
kubectl get pvc -n todo-app

echo ""
echo "Recent Events:"
kubectl get events -n todo-app --sort-by='.lastTimestamp' | tail -10

echo ""
echo "========================================="
echo "To view logs:"
echo "  kubectl logs -n todo-app deployment/backend"
echo "  kubectl logs -n todo-app deployment/chatbot"
echo "  kubectl logs -n todo-app deployment/frontend"
echo "  kubectl logs -n todo-app deployment/ollama"
echo "========================================="
