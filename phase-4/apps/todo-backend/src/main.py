"""
FastAPI application main entry point.

Configures the FastAPI app with CORS middleware, routes, and middleware.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.database import DatabaseManager, init_db

# Load environment variables from .env file
_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=_env_path)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI app.

    Handles startup and shutdown events.
    """
    # Scheduler instance
    scheduler = None

    # Startup
    print(f"Starting Todo App API")
    print(f"Environment: {settings.env}")
    print(f"Database: {settings.database_url.split('@')[-1]}")

    # Initialize database (create tables if not exists)
    # In production, use Alembic migrations instead
    if settings.is_development:
        init_db()
        print("Database initialized")

    # Start reminder scheduler if Gmail configured
    if settings.gmail_email and settings.gmail_app_password:
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from src.services.reminder_service import check_and_send_reminders
            from src.core.database import get_session

            scheduler = AsyncIOScheduler()

            # Add job to check reminders every hour
            def run_reminder_check():
                """Wrapper to get fresh session for each check."""
                session = next(get_session())
                try:
                    check_and_send_reminders(session)
                finally:
                    session.close()

            scheduler.add_job(
                run_reminder_check,
                'interval',
                hours=1,
                id='reminder_checker',
                name='Check and send task reminders'
            )
            scheduler.start()
            print("[OK] Reminder scheduler started (runs every hour)")
        except Exception as e:
            print(f"[WARN] Failed to start reminder scheduler: {e}")
    else:
        print("[WARN] Reminder scheduler disabled (Gmail not configured)")

    yield

    # Shutdown
    if scheduler:
        scheduler.shutdown()
        print("Reminder scheduler stopped")
    print("Shutting down Todo App API")


# Create FastAPI app
app = FastAPI(
    title='Todo App API',
    description='Premium Todo SaaS Application API',
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    print(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            'detail': 'Internal server error',
            'message': str(exc) if settings.is_development else 'An error occurred',
        },
    )


# Health check endpoint
@app.get('/health', tags=['Health'])
async def health_check():
    """
    Health check endpoint.

    Returns API status and database connection status.
    """
    db_connected = DatabaseManager.check_connection()

    return {
        'status': 'healthy',
        'api': 'Todo App API',
        'version': '0.1.0',
        'environment': settings.env,
        'database': 'connected' if db_connected else 'disconnected',
    }


# Root endpoint
@app.get('/', tags=['Root'])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        'message': 'Welcome to Todo App API',
        'version': '0.1.0',
        'docs': '/docs',
        'health': '/health',
    }


# Include routers
from src.api import auth, todos, users, ai, chat

app.include_router(auth.router, prefix='/api/auth', tags=['Authentication'])
app.include_router(todos.router, prefix='/api/todos', tags=['Todos'])
app.include_router(users.router, prefix='/api/users', tags=['Users'])
app.include_router(ai.router, prefix='/api/ai', tags=['AI'])
# T010: Added AI chat router for dashboard integration with /api/ai-chat prefix
app.include_router(chat.router, tags=['AI Chat'])  # Router has /api/ai-chat prefix defined in chat.py


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'src.main:app',
        host='0.0.0.0',
        port=settings.port,
        reload=settings.is_development,
    )
