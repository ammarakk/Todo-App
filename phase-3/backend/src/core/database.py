"""
Database configuration and session management.

Provides SQLAlchemy engine with connection pooling and session dependency for FastAPI.
"""
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel

from src.core.config import settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    str(settings.database_url),
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Additional connections when pool is full
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.is_development,  # Log SQL in development
)


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should only be used for development/testing.
    In production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.

    Yields a database session and ensures it's closed after use.
    Automatically handles rollback on errors.

    Yields:
        Session: SQLAlchemy session

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_session)):
            return db.exec(select(User)).all()
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseManager:
    """
    Database manager for advanced operations.

    Provides methods for health checks, connection testing,
    and administrative tasks.
    """

    @staticmethod
    def check_connection() -> bool:
        """
        Check if database connection is alive.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    @staticmethod
    def get_pool_status() -> dict:
        """
        Get connection pool status.

        Returns:
            dict: Pool statistics including size, checked out, and overflow
        """
        pool = engine.pool
        return {
            'pool_size': pool.size(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'max_overflow': engine.pool.max_overflow,
        }


# Export for use in other modules
__all__ = ['engine', 'get_session', 'init_db', 'DatabaseManager']
