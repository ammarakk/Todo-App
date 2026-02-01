#!/bin/bash
# Phase IV Docker Stop Script
# Stops all Docker services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/infra/docker/docker-compose.yml"

echo "========================================="
echo "Phase IV - Stopping Docker Services"
echo "========================================="

cd "$PROJECT_ROOT/infra/docker"

echo ""
echo "Stopping services..."
docker-compose -f "$COMPOSE_FILE" down

echo ""
echo "========================================="
echo "Services Stopped!"
echo ""
echo "To start again: ./scripts/docker-start.sh"
echo "========================================="
