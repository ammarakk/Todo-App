"""
Security utilities for authentication and password management.

Provides password hashing with bcrypt and JWT token creation/verification.
"""
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import hashlib
from jose import JWTError, jwt

from src.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Supports both old direct bcrypt and new SHA256+bcrypt hashes.
    """
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password

    # Try new method (SHA256 + bcrypt) first
    try:
        password_hash = hashlib.sha256(plain_password.encode('utf-8')).digest()
        if bcrypt.checkpw(password_hash, hashed_bytes):
            return True
    except:
        pass

    # Try old method (direct bcrypt) for backward compatibility
    try:
        password_bytes = plain_password.encode('utf-8')[:72]
        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return True
    except:
        pass

    return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    # Hash the password with SHA256 first to avoid bcrypt's 72-byte limit
    # This is a safe and common practice
    password_hash = hashlib.sha256(password.encode('utf-8')).digest()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {'sub': user_id})
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        token = create_access_token(data={'sub': str(user.id)})
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_expiration_days)

    to_encode.update({'exp': expire})

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        dict: Decoded token payload if valid, None if invalid

    Example:
        payload = decode_access_token(token)
        if payload:
            user_id = payload.get('sub')
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


class TokenData:
    """
    Token data model for decoded JWT tokens.

    Attributes:
        user_id: User ID from token subject
        exp: Token expiration timestamp
    """

    def __init__(self, user_id: Optional[str] = None, exp: Optional[int] = None):
        self.user_id = user_id
        self.exp = exp

    @classmethod
    def from_token(cls, token: str) -> Optional['TokenData']:
        """
        Create TokenData from JWT token.

        Args:
            token: JWT token to decode

        Returns:
            TokenData if token is valid, None otherwise
        """
        payload = decode_access_token(token)
        if payload is None:
            return None

        user_id = payload.get('sub')
        exp = payload.get('exp')

        return cls(user_id=user_id, exp=exp)

    def is_expired(self) -> bool:
        """
        Check if token is expired.

        Returns:
            bool: True if token is expired, False otherwise
        """
        if self.exp is None:
            return False

        return datetime.utcnow().timestamp() > self.exp


# Export for use in other modules
__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'decode_access_token',
    'TokenData',
]
