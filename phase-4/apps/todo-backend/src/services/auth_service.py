"""
Authentication service for user management.

Provides functions for user creation, authentication, and JWT token management.
"""
import re
from typing import Optional
from uuid import UUID

from jose import JWTError
from sqlmodel import Session, select

from src.core.config import settings
from src.core.security import create_access_token, verify_password
from src.models.user import User
from src.schemas.user import UserCreate


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password

    Raises:
        ValueError: If password doesn't meet requirements
    """
    if not password or len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')

    if not re.search(r'[A-Za-z]', password):
        raise ValueError('Password must contain at least one letter')

    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one number')

    from src.core.security import get_password_hash

    return get_password_hash(password)


def check_email_exists(db: Session, email: str) -> bool:
    """
    Check if an email already exists in the database.

    Args:
        db: Database session
        email: Email to check

    Returns:
        bool: True if email exists, False otherwise
    """
    user = db.exec(select(User).where(User.email.ilike(email))).first()
    return user is not None


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        User: Created user object

    Raises:
        ValueError: If email already exists or password is invalid
    """
    # Check if email already exists (case-insensitive)
    if check_email_exists(db, user_data.email):
        raise ValueError(f'Email {user_data.email} is already registered')

    # Hash password
    try:
        password_hash = hash_password(user_data.password)
    except ValueError as e:
        raise ValueError(str(e))

    # Create new user
    user = User(
        name=user_data.name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=password_hash,
    )

    # Save to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User's email
        password: Plain text password

    Returns:
        User: User object if authentication successful, None otherwise
    """
    # Find user by email (case-insensitive)
    user = db.exec(select(User).where(User.email.ilike(email))).first()

    if not user:
        return None

    # Verify password (truncation is handled in verify_password function)
    if not verify_password(password, user.password_hash):
        return None

    return user


def create_user_token(user_id: UUID) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User's UUID

    Returns:
        str: JWT access token

    Raises:
        ValueError: If token creation fails
    """
    try:
        token = create_access_token(data={'sub': str(user_id)})
        return token
    except JWTError as e:
        raise ValueError(f'Failed to create access token: {str(e)}')


def verify_user_token(token: str) -> Optional[UUID]:
    """
    Verify a JWT token and extract user ID.

    Args:
        token: JWT access token

    Returns:
        UUID: User ID if token is valid, None otherwise
    """
    from src.core.security import decode_access_token, TokenData

    try:
        token_data = TokenData.from_token(token)
        if token_data and token_data.user_id and not token_data.is_expired():
            return UUID(token_data.user_id)
    except (JWTError, ValueError):
        return None

    return None


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        User: User object if found, None otherwise
    """
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: User's email

    Returns:
        User: User object if found, None otherwise
    """
    return db.exec(select(User).where(User.email.ilike(email))).first()


# Export for use in other modules
__all__ = [
    'hash_password',
    'check_email_exists',
    'create_user',
    'authenticate_user',
    'create_user_token',
    'verify_user_token',
    'get_user_by_id',
    'get_user_by_email',
]
