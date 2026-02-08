#!/bin/bash
# Fix HuggingFace Space Secrets for AI Chat
# Sets the correct AI provider and API key

SPACE_REPO="ammaraak/todo-backend-new"

echo "Setting secrets on HuggingFace Space: $SPACE_REPO"
echo ""

# Set AI_PROVIDER to gemini
echo "Setting AI_PROVIDER=gemini..."
echo "gemini" | hf secrets set AI_PROVIDER --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set AI_PROVIDER"

# Set GEMINI_API_KEY (user provided key)
echo "Setting GEMINI_API_KEY..."
echo "AIzaSyCWV3opImJIT_KhSyti9qdGTnxC_pPnca4" | hf secrets set GEMINI_API_KEY --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set GEMINI_API_KEY"

# DATABASE_URL (already set, keeping for completeness)
echo "DATABASE_URL already set (skipping)"

# JWT_SECRET
echo "Setting JWT_SECRET..."
echo "your-super-secret-jwt-key-min-32-characters-long" | hf secrets set JWT_SECRET --repo-type space --repo $SPACE_REPO 2>&1 || echo "Failed to set JWT_SECRET"

echo ""
echo "Done! Secrets configured on HuggingFace Space."
echo "The space will restart automatically."
echo ""
echo "AI Configuration:"
echo "  AI_PROVIDER: gemini"
echo "  GEMINI_API_KEY: ***set***"
