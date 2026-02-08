#!/bin/bash
# Set HuggingFace Space Secrets

SPACE_REPO="ammaraak/todo-api"

echo "Setting secrets on HuggingFace Space..."

# Set QWEN_API_KEY
echo "Setting QWEN_API_KEY..."
echo "0XA2TcDarwQtRtWP-uwkwY2L3PCkWHFuzQkxWyW1r2Xm58q5dR81tBuQSTAvW7AKppM8D0GRseYZb8AZ-cMtiQ" | hf secrets set QWEN_API_KEY --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set QWEN_API_KEY"

# Set USE_QWEN_API
echo "Setting USE_QWEN_API..."
echo "true" | hf secrets set USE_QWEN_API --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set USE_QWEN_API"

# Set DATABASE_URL
echo "Setting DATABASE_URL..."
echo "postgresql+psycopg://neondb_owner:npg_ChtFeYRd02nq@ep-lucky-meadow-abpkcyn6-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require" | hf secrets set DATABASE_URL --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set DATABASE_URL"

echo "Done! Secrets set on HuggingFace Space."
