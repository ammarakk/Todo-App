"""
Prometheus Metrics - Phase 5
Production monitoring and observability
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps
from typing import Callable
from src.utils.logger import get_logger

logger = get_logger(__name__)

# API Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint']
)

# Business Metrics
tasks_created_total = Counter(
    'tasks_created_total',
    'Total tasks created',
    ['user_id']
)

tasks_completed_total = Counter(
    'tasks_completed_total',
    'Total tasks completed',
    ['user_id']
)

tasks_deleted_total = Counter(
    'tasks_deleted_total',
    'Total tasks deleted',
    ['user_id']
)

reminders_sent_total = Counter(
    'reminders_sent_total',
    'Total reminders sent',
    ['delivery_method', 'status']
)

recurring_tasks_generated_total = Counter(
    'recurring_tasks_generated_total',
    'Total recurring task occurrences generated',
    ['pattern']
)

ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['agent', 'intent', 'status']
)

ai_confidence_score = Histogram(
    'ai_confidence_score',
    'AI confidence score distribution',
    ['intent'],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Database Metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table']
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

# Kafka/Dapr Metrics
kafka_messages_published_total = Counter(
    'kafka_messages_published_total',
    'Total Kafka messages published',
    ['topic', 'status']
)

kafka_message_publish_duration_seconds = Histogram(
    'kafka_message_publish_duration_seconds',
    'Kafka message publish latency',
    ['topic'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections',
    ['user_id']
)

websocket_messages_sent_total = Counter(
    'websocket_messages_sent_total',
    'Total WebSocket messages sent',
    ['message_type']
)

# System Metrics
app_info = Info(
    'app',
    'Application information'
)

scheduler_status = Gauge(
    'scheduler_status',
    'Background scheduler status (1=running, 0=stopped)',
    ['scheduler_name']
)

cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

external_api_requests_total = Counter(
    'external_api_requests_total',
    'Total external API requests',
    ['service', 'status']
)

external_api_duration_seconds = Histogram(
    'external_api_duration_seconds',
    'External API request latency',
    ['service'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)


def track_endpoint(endpoint: str = None):
    """
    Decorator to track HTTP request metrics.

    Usage:
    @track_endpoint("tasks")
    async def get_tasks(...):
        ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract method and endpoint
            method = kwargs.get('_method', 'GET')
            endpoint_name = endpoint or func.__name__

            # Track in-progress
            http_requests_in_progress.labels(
                method=method,
                endpoint=endpoint_name
            ).inc()

            start_time = time.time()
            status = 'success'

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                errors_total.labels(
                    error_type=type(e).__name__,
                    endpoint=endpoint_name
                ).inc()
                raise
            finally:
                # Track duration
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint_name
                ).observe(duration)

                # Track request count
                http_requests_total.labels(
                    method=method,
                    endpoint=endpoint_name,
                    status=status
                ).inc()

                # Decrease in-progress
                http_requests_in_progress.labels(
                    method=method,
                    endpoint=endpoint_name
                ).dec()

        return wrapper
    return decorator


def track_db_query(operation: str, table: str):
    """
    Decorator to track database query metrics.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)

                db_queries_total.labels(
                    operation=operation,
                    table=table
                ).inc()

        return wrapper
    return decorator


def track_ai_request(agent: str, intent: str):
    """
    Decorator to track AI request metrics.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            status = 'success'
            confidence = 0.0

            try:
                result = await func(*args, **kwargs)

                # Extract confidence if available
                if isinstance(result, dict):
                    confidence = result.get('confidence', 0.0)

                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                ai_requests_total.labels(
                    agent=agent,
                    intent=intent,
                    status=status
                ).inc()

                if confidence > 0:
                    ai_confidence_score.labels(intent=intent).observe(confidence)

        return wrapper
    return decorator


def get_metrics() -> Response:
    """
    Endpoint to expose Prometheus metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def initialize_app_info(version: str, environment: str):
    """
    Initialize application info metrics.
    """
    app_info.info({
        'version': version,
        'environment': environment
    })
