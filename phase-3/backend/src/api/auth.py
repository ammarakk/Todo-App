"""
Authentication API routes.

Provides endpoints for user registration, login, logout, and token verification.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.api.deps import get_current_user, get_db
from src.core.config import settings
from src.models.user import User
from src.schemas.auth import AuthResponse, LoginRequest, SignupRequest
from src.schemas.user import UserResponse
from src.services.auth_service import (
    authenticate_user,
    create_user,
    create_user_token,
    get_user_by_email,
)

router = APIRouter()


@router.post(
    '/signup',
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Register a new user',
    description='Create a new user account with email and password',
)
async def signup(
    user_data: SignupRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Validates email format, checks for duplicate emails,
    validates password strength, and creates a new user.

    Args:
        user_data: User registration data (name, email, password)
        db: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException 400: If validation fails or email already exists
    """
    print(f"DEBUG: Signup request received: {user_data.dict()}")
    try:
        # Create user
        user = create_user(db, user_data)

        # Generate JWT token
        access_token = create_user_token(user.id)

        # Return response
        return AuthResponse(
            access_token=access_token,
            token_type='bearer',
            user={
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'avatar_url': user.avatar_url,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat(),
            },
        )

    except ValueError as e:
        # Handle validation errors
        error_msg = str(e)

        if 'already registered' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email is already registered. Please use a different email or login.',
            )
        elif 'Password' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Validation failed: ' + error_msg,
            )

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while creating your account. Please try again.',
        )


@router.post(
    '/login',
    response_model=AuthResponse,
    summary='Login user',
    description='Authenticate user with email and password',
)
async def login(
    user_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Login a user.

    Validates credentials and returns a JWT token.

    Args:
        user_data: Login credentials (email, password)
        response: FastAPI response object
        db: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    print(f"DEBUG: Login request received: email={user_data.email}")
    # Authenticate user
    user = authenticate_user(db, user_data.email, user_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Generate JWT token
    access_token = create_user_token(user.id)

    # Set httpOnly cookie (optional, for additional security)
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=not settings.is_development,  # HTTPS in production
        samesite='lax',
        max_age=settings.jwt_expiration_days * 24 * 60 * 60,  # Convert days to seconds
    )

    # Return response
    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
        user={
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
        },
    )


@router.post(
    '/logout',
    summary='Logout user',
    description='Logout user and clear authentication token',
)
async def logout(response: Response):
    """
    Logout a user.

    Clears the authentication cookie.

    Args:
        response: FastAPI response object

    Returns:
        dict: Logout confirmation message
    """
    # Clear authentication cookie
    response.delete_cookie('access_token')

    return {'message': 'Successfully logged out'}


@router.get(
    '/me',
    response_model=UserResponse,
    summary='Get current user',
    description='Get information about the currently authenticated user',
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current authenticated user.

    Requires valid JWT token in Authorization header.

    Args:
        current_user: Current user from dependency

    Returns:
        UserResponse: Current user information
    """
    return current_user


# OAuth2 compatible endpoint for token generation
@router.post(
    '/token',
    response_model=AuthResponse,
    summary='Get access token',
    description='OAuth2 compatible endpoint to get access token',
)
async def get_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token endpoint.

    Used by OAuth2 clients to obtain access tokens.

    Args:
        form_data: OAuth2 password request form
        response: FastAPI response object
        db: Database session

    Returns:
        AuthResponse: JWT token and user information
    """
    # Use login logic
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_user_token(user.id)

    # Set cookie
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=not settings.is_development,
        samesite='lax',
        max_age=settings.jwt_expiration_days * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=access_token,
        token_type='bearer',
        user={
            'id': str(user.id),
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat(),
        },
    )


# Export router
__all__ = ['router']
