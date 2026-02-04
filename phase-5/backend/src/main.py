"""
FastAPI Main Application - Phase 5 Backend
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import chat, health, reminders_api
from src.api import chat_orchestrator, tasks_api, recurring_tasks_api, recurring_subscription, websocket
from src.utils.config import settings
from src.utils.logging import configure_logging, get_logger
from src.utils.errors import error_handler
from src.utils.middleware import CorrelationIdMiddleware, RequestLoggingMiddleware
from src.utils.database import init_database, close_database
from src.services import start_scheduler, stop_scheduler
from src.services.websocket_broadcaster import start_broadcaster, stop_broadcaster

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("application_starting", version=settings.app_version)

    # Initialize database (optional - can be done via migrations)
    # await init_database()

    # Start reminder scheduler
    await start_scheduler()
    logger.info("reminder_scheduler_started")

    # Start WebSocket broadcaster
    await start_broadcaster()
    logger.info("websocket_broadcaster_started")

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Stop WebSocket broadcaster
    await stop_broadcaster()
    logger.info("websocket_broadcaster_stopped")

    # Stop reminder scheduler
    await stop_scheduler()
    logger.info("reminder_scheduler_stopped")

    # await close_database()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Todo Application with Dapr and Kafka",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Register error handler
app.exception_handler(Exception)(error_handler)

# Include routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(chat_orchestrator.router)
app.include_router(tasks_api.router)
app.include_router(reminders_api.router)
app.include_router(recurring_tasks_api.router)
app.include_router(recurring_subscription.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Phase 5 Todo Backend",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.app_env == "local",
    )
