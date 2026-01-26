# Implements: T010
# Phase III - AI-Powered Todo Chatbot
# JWT Verification Middleware - Extracts user_id and rejects invalid tokens

from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from src.core.config import settings


# JWT Configuration
JWT_SECRET = settings.jwt_secret
JWT_ALGORITHM = settings.jwt_algorithm

# Security scheme for FastAPI
security = HTTPBearer()


async def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify JWT token and extract user_id.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        user_id: Extracted user UUID from JWT token

    Raises:
        HTTPException 401: If token is invalid, expired, or malformed
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Extract user_id from payload
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
            )

        return user_id

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Dependency injection helper to get current user_id from JWT.

    Usage in FastAPI endpoints:
        user_id = await get_current_user_id(credentials)

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        user_id: Extracted user UUID
    """
    return await verify_jwt(credentials)
