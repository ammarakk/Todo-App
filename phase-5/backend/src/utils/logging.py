"""
Structured JSON Logging with structlog
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from .config import settings


def add_correlation_id(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add correlation ID to log entry if available"""
    # This will be populated by middleware
    import contextvars
    correlation_id = contextvars.ContextVar("correlation_id", default=None)
    if correlation_id:
        event_dict["correlation_id"] = correlation_id.get()
    return event_dict


def drop_color_message_key(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Drop color key for non-dev environments"""
    event_dict.pop("color_message", None)
    return event_dict


def configure_logging() -> None:
    """Configure structured JSON logging"""
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        add_correlation_id,
    ]
    
    if settings.app_env == "local":
        # Development: Pretty console output
        renderer = structlog.dev.ConsoleRenderer(
            colors=settings.debug,
            exception_formatter=structlog.dev.plain_traceback
        )
    else:
        # Production: JSON output
        renderer = structlog.processors.JSONRenderer()
        shared_processors.append(drop_color_message_key)
    
    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_renderer(renderer)],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Silence noisy loggers
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger"""
    return structlog.get_logger(name)
