"""
Middleware for correlation ID and request tracking
"""
import contextvars
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import settings
from .logging import get_logger

correlation_id_ctx = contextvars.ContextVar("correlation_id", default=None)
logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Add correlation ID to requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation ID
        correlation_id = request.headers.get(
            settings.correlation_id_header,
            str(uuid.uuid4())
        )
        
        # Store in context
        correlation_id_ctx.set(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers[settings.correlation_id_header] = correlation_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with timing"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        return response
