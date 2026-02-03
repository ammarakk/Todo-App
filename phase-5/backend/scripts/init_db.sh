#!/bin/bash
# Initialize Neon Database
# Usage: ./scripts/init_db.sh

set -e

echo "🚀 Initializing Neon Database..."

# Database connection
DB_URL="postgresql://neondb_owner:npg_4oK0utXaHpci@ep-broad-darkness-abnsobdy-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found. Please install PostgreSQL client"
    exit 1
fi

echo "📊 Running schema migration..."
psql "$DB_URL" -f src/utils/database/schema.sql

echo "✅ Database initialized successfully!"
echo ""
echo "📝 Tables created:"
echo "  - users"
echo "  - tasks"
echo "  - reminders"
echo "  - conversations"
echo "  - messages"
echo "  - events"
echo "  - audit_logs"
