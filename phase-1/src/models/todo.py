"""Todo entity and status enum."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TodoStatus(Enum):
    """Status of a todo item."""

    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Todo:
    """Represents a unit of work to be tracked.

    This entity is designed to evolve cleanly from in-memory storage
    (Phase I) to SQLModel database persistence (Phase II).
    """

    id: int
    title: str
    description: Optional[str]
    status: TodoStatus
    created_at: datetime
