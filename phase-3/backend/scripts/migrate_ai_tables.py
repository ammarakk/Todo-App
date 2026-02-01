# Implements: T009, T006
# Phase III - AI-Powered Todo Chatbot
# Database Migration Script - Creates Conversation and Message tables

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel, create_engine
# Import with absolute path from project root
from backend.src.models.user import User
# Temporarily exclude Todo model because SQLite doesn't support ARRAY type
# Todo model is for Phase II and will work with Neon PostgreSQL
# from backend.src.models.todo import Todo
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from dotenv import load_dotenv

# Load environment variables from project root
env_path = project_root / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("NEON_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "NEON_DATABASE_URL not found in environment variables. "
        "Please set it in your .env file."
    )

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


def migrate():
    """Create Conversation and Message tables in Neon PostgreSQL"""
    print("[OK] Checking database connection...")

    # Test connection
    with engine.connect() as conn:
        pass

    print("[OK] Creating Conversation table...")
    # Conversation table will be created with indexes

    print("[OK] Creating Message table...")
    # Message table will be created with indexes

    print("[OK] Creating tables with indexes...")

    # Create all tables defined in SQLModel metadata
    SQLModel.metadata.create_all(engine)

    print("[OK] Migration complete!")
    print("\nTables created:")
    print("  - conversation (with index on user_id)")
    print("  - message (with index on conversation_id and created_at)")


if __name__ == "__main__":
    migrate()
