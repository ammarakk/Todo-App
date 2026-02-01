#!/bin/bash
# Phase IV Kubernetes Delete Script
# Deletes the application from Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/infra/k8s"

echo "========================================="
echo "Phase IV - Deleting from Kubernetes"
echo "========================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl not found."
    exit 1
fi

echo ""
echo "This will delete all Phase IV resources from namespace 'todo-app'."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Deleting resources..."
kubectl delete -f "$K8S_DIR/04-frontend.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/03-chatbot.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/02-backend.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/01-ollama.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/00-postgres.yaml" --ignore-not-found=true
kubectl delete -f "$K8S_DIR/namespace.yaml" --ignore-not-found=true

echo ""
echo "========================================="
echo "Deletion Complete!"
echo "========================================="
