"""
User Model
"""
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class User(BaseModel):
    """User account"""
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
