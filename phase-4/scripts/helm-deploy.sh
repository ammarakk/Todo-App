#!/bin/bash
# Phase IV Helm Deploy Script
# Deploys the application using Helm

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HELM_CHART="$PROJECT_ROOT/infra/helm/todo-app"
RELEASE_NAME="todo-app"
NAMESPACE="todo-app"

echo "========================================="
echo "Phase IV - Deploying with Helm"
echo "========================================="

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "Error: helm not found. Please install helm first."
    exit 1
fi

# Check cluster connection
echo ""
echo "Checking cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    exit 1
fi

echo "Cluster connected successfully."

# Create namespace if it doesn't exist
echo ""
echo "Ensuring namespace exists..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Check if release exists
if helm release list -n "$NAMESPACE" 2>/dev/null | grep -q "$RELEASE_NAME"; then
    echo ""
    echo "Release '$RELEASE_NAME' exists. Upgrading..."
    helm upgrade "$RELEASE_NAME" "$HELM_CHART" --namespace "$NAMESPACE"
else
    echo ""
    echo "Installing new release..."
    helm install "$RELEASE_NAME" "$HELM_CHART" --namespace "$NAMESPACE"
fi

echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n "$NAMESPACE" --timeout=60s || true
kubectl wait --for=condition=ready pod -l app=ollama -n "$NAMESPACE" --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=backend -n "$NAMESPACE" --timeout=60s || true
kubectl wait --for=condition=ready pod -l app=chatbot -n "$NAMESPACE" --timeout=60s || true
kubectl wait --for=condition=ready pod -l app=frontend -n "$NAMESPACE" --timeout=60s || true

echo ""
echo "========================================="
echo "Deployment Complete!"
echo ""
echo "Helm Release:"
helm status "$RELEASE_NAME" -n "$NAMESPACE"

echo ""
echo "Pods:"
kubectl get pods -n "$NAMESPACE"

echo ""
echo "========================================="
echo "To access the application:"
echo "1. For local development, use port-forward:"
echo "   kubectl port-forward -n $NAMESPACE svc/frontend-service 3000:3000"
echo ""
echo "2. For production, configure an Ingress controller"
echo ""
echo "Upgrade: helm upgrade $RELEASE_NAME $HELM_CHART -n $NAMESPACE"
echo "Uninstall: helm uninstall $RELEASE_NAME -n $NAMESPACE"
echo "========================================="
