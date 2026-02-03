"""
Security utilities for authentication and password management.

Provides password hashing with bcrypt and JWT token creation/verification.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


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
