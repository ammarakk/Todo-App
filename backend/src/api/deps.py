"""
FastAPI dependencies for database sessions and authentication.

Provides reusable dependency functions for injecting database sessions
and authenticated users into route handlers.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from src.core.database import get_session
from src.core.security import TokenData
from src.models.user import User

# HTTP Bearer token scheme for JWT extraction
security = HTTPBearer(auto_error=False)


async def get_db(
    session: Session = Depends(get_session),
) -> Session:
    """
    Dependency for getting database session.

    This is a passthrough dependency that allows for future enhancements
    like request-scoped sessions or transaction management.

    Args:
        session: Database session from get_session

    Returns:
        Session: Database session

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.exec(select(User)).all()
    """
    return session


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency for getting authenticated user from JWT token.

    Extracts JWT token from Authorization header, validates it,
    and returns the corresponding user.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If token is missing, invalid, or user not found

    Example:
        @app.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    # Check if credentials are provided
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Extract and decode token
    token = credentials.credentials
    token_data = TokenData.from_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Check if token is expired
    if token_data.is_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Get user from database
    user = db.get(User, token_data.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Optional authentication dependency.

    Returns the authenticated user if a valid token is provided,
    otherwise returns None. Useful for routes that work for both
    authenticated and anonymous users.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        Optional[User]: Authenticated user or None

    Example:
        @app.get("/public-data")
        def get_public_data(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return {'data': '...', 'user': user.email}
            return {'data': '...'}
    """
    if credentials is None:
        return None

    token = credentials.credentials
    token_data = TokenData.from_token(token)

    if token_data is None or token_data.is_expired():
        return None

    user = db.get(User, token_data.user_id)
    return user


async def get_current_user_id(
    current_user: User = Depends(get_current_user),
) -> str:
    """
    Dependency for getting authenticated user's ID as a string.

    This is a convenience wrapper around get_current_user that extracts
    just the user ID as a string, which is commonly needed in API routes.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        str: User ID as a string

    Example:
        @app.get("/todos")
        def list_todos(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}
    """
    return str(current_user.id)


# Export for use in other modules
__all__ = ['get_db', 'get_current_user', 'get_current_user_optional', 'get_current_user_id']
