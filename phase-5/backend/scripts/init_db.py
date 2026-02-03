"""
Initialize Neon Database with Python
Run: python scripts/init_db.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Base
from src.utils.config import settings
from src.utils.logging import configure_logging, get_logger

# Use Neon database
NEON_DB_URL = "postgresql+asyncpg://neondb_owner:npg_4oK0utXaHpci@ep-broad-darkness-abnsobdy-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

configure_logging()
logger = get_logger(__name__)


async def init_database():
    """Initialize database schema"""
    logger.info("🚀 Initializing Neon Database...")
    
    # Create async engine for Neon
    engine = create_async_engine(
        NEON_DB_URL,
        echo=True,
    )
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully!")
        logger.info("📝 Tables created:")
        for table in Base.metadata.tables.keys():
            logger.info(f"  - {table}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
