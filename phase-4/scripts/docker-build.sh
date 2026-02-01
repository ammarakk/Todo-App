#!/bin/bash
# Phase IV Docker Build Script
# Builds all Docker images for the Todo application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Phase IV - Building Docker Images"
echo "========================================="

cd "$PROJECT_ROOT"

# Build Backend
echo ""
echo "Building Backend Image..."
cd apps/todo-backend
docker build -t todo-backend:latest .
cd "$PROJECT_ROOT"

# Build Chatbot
echo ""
echo "Building Chatbot Image..."
cd apps/chatbot
docker build -t todo-chatbot:latest .
cd "$PROJECT_ROOT"

# Build Frontend
echo ""
echo "Building Frontend Image..."
cd apps/todo-frontend
docker build -t todo-frontend:latest .
cd "$PROJECT_ROOT"

echo ""
echo "========================================="
echo "Build Complete!"
echo "Images:"
echo "  - todo-backend:latest"
echo "  - todo-chatbot:latest"
echo "  - todo-frontend:latest"
echo "  - ollama/ollama:latest (pulled on first run)"
echo "========================================="
