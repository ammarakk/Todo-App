# Todo Backend (Phase III)

## ⚠️ READ-ONLY - PHASE IV PROTECTION

**This directory is a READ-ONLY copy of Phase III backend code.**

## Constitution Reference

Per Phase IV Principle VII: **Immutable Phase III Business Logic**

## What CAN Be Modified

Environment variable configurations (via `.env` files):
- DATABASE_URL - PostgreSQL connection string (injected by Kubernetes)
- JWT_SECRET - JWT signing key (injected via Kubernetes Secrets)
- OLLAMA_HOST - Ollama service endpoint (for chatbot integration)
- PORT - Server port (default: 8000)

## What CANNOT Be Modified

- ❌ Business logic in src/
- ❌ Database models or schemas
- ❌ API endpoints or routes
- ❌ Authentication logic
- ❌ MCP tools or integrations

## Original Location

This code was copied from: phase-3/backend/
