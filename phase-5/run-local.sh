#!/bin/bash
# Run Phase 5 Backend Locally

set -e

echo "🚀 Starting Phase 5 Backend..."

cd backend

# Activate virtual environment (if exists)
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Start application
echo "🎯 Starting server on http://localhost:8000"
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
