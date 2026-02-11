"""
User API routes.

Provides endpoints for user profile management.
"""
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from sqlmodel import Session, select, func
from datetime import datetime

from src.api.deps import get_current_user_id, get_db
from src.models.user import User
from src.models.todo import Todo, Status
from src.schemas.user import UserResponse, UserProfileUpdateRequest

router = APIRouter()


@router.get(
    '/me',
    response_model=dict,
    summary='Get current user profile',
    description='Get current user profile with statistics',
)
async def get_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Get current user profile with todo statistics."""
    # Get user
    query = select(User).where(User.id == UUID(current_user_id))
    user = db.exec(query).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )

    # Get todo statistics
    total_todos = db.exec(
        select(func.count()).select_from(Todo).where(Todo.user_id == user.id)
    ).one()
    pending_todos = db.exec(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == user.id,
            Todo.status == Status.PENDING
        )
    ).one()
    completed_todos = db.exec(
        select(func.count()).select_from(Todo).where(
            Todo.user_id == user.id,
            Todo.status == Status.COMPLETED
        )
    ).one()

    return {
        'id': str(user.id),
        'name': user.name,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
        'stats': {
            'total_todos': total_todos,
            'pending_todos': pending_todos,
            'completed_todos': completed_todos,
        }
    }


@router.patch(
    '/me',
    response_model=dict,
    summary='Update user profile',
    description='Update current user profile',
)
async def update_profile(
    profile_data: UserProfileUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    # Get user
    query = select(User).where(User.id == UUID(current_user_id))
    user = db.exec(query).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )

    # Update fields
    if profile_data.name is not None:
        user.name = profile_data.name
    user.updated_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        'id': str(user.id),
        'name': user.name,
        'email': user.email,
        'avatar_url': user.avatar_url,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


@router.post(
    '/me/avatar',
    response_model=dict,
    summary='Upload avatar',
    description='Upload user avatar image',
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """Upload user avatar."""
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid file type. Allowed: {", ".join(allowed_types)}',
        )

    # Validate file size (5MB max)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File too large. Maximum size: 5MB',
        )

    # For now, return a placeholder avatar URL
    # In production, you would upload to Cloudinary here
    from src.core.config import settings

    if settings.cloudinary_cloud_name:
        # TODO: Implement Cloudinary upload
        avatar_url = f"https://ui-avatars.com/api/?name={file.filename}&background=random"
    else:
        # Use UI Avatars as fallback
        query = select(User).where(User.id == UUID(current_user_id))
        user = db.exec(query).first()
        avatar_url = f"https://ui-avatars.com/api/?name={user.name}&background=random"

    # Update user avatar
    query = select(User).where(User.id == UUID(current_user_id))
    user = db.exec(query).first()

    if user:
        user.avatar_url = avatar_url
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()

    return {
        'avatar_url': avatar_url,
        'message': 'Avatar uploaded successfully',
    }


__all__ = ['router']
