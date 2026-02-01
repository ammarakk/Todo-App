#!/bin/bash
# Phase IV Kubernetes Deploy Script
# Deploys the application to Kubernetes using kubectl

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/infra/k8s"

echo "========================================="
echo "Phase IV - Deploying to Kubernetes"
echo "========================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl not found. Please install kubectl first."
    exit 1
fi

# Check cluster connection
echo ""
echo "Checking cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    echo "Please ensure your cluster is running and kubeconfig is configured."
    exit 1
fi

echo "Cluster connected successfully."

# Create namespace
echo ""
echo "Creating namespace..."
kubectl apply -f "$K8S_DIR/namespace.yaml"

# Deploy in order
echo ""
echo "Deploying PostgreSQL..."
kubectl apply -f "$K8S_DIR/00-postgres.yaml"

echo ""
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=60s

echo ""
echo "Deploying Ollama..."
kubectl apply -f "$K8S_DIR/01-ollama.yaml"

echo ""
echo "Waiting for Ollama to be ready..."
kubectl wait --for=condition=ready pod -l app=ollama -n todo-app --timeout=120s

echo ""
echo "Deploying Backend..."
kubectl apply -f "$K8S_DIR/02-backend.yaml"

echo ""
echo "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n todo-app --timeout=60s

echo ""
echo "Deploying Chatbot..."
kubectl apply -f "$K8S_DIR/03-chatbot.yaml"

echo ""
echo "Waiting for Chatbot to be ready..."
kubectl wait --for=condition=ready pod -l app=chatbot -n todo-app --timeout=60s

echo ""
echo "Deploying Frontend..."
kubectl apply -f "$K8S_DIR/04-frontend.yaml"

echo ""
echo "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n todo-app --timeout=60s

echo ""
echo "========================================="
echo "Deployment Complete!"
echo ""
echo "Services:"
kubectl get svc -n todo-app
echo ""
echo "Pods:"
kubectl get pods -n todo-app
echo ""
echo "========================================="
echo "To access the application:"
echo "1. For local development, use port-forward:"
echo "   kubectl port-forward -n todo-app svc/frontend-service 3000:3000"
echo ""
echo "2. For production, configure an Ingress controller"
echo "========================================="
