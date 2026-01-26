# Implements: T011
# Phase III - AI-Powered Todo Chatbot
# FastAPI Main Application - Entry point for backend server

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import Phase III components
from src.api.chat import router as chat_router
from src.middleware.auth import get_current_user_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Phase III AI-Powered Todo Chatbot backend...")
    logger.info(f"Qwen Model: {os.getenv('QWEN_MODEL', 'Qwen/Qwen-14B-Chat')}")
    logger.info(f"Server: {os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8000')}")

    yield

    # Shutdown
    logger.info("Shutting down Phase III backend...")


# Create FastAPI application
app = FastAPI(
    title="Phase III - AI-Powered Todo Chatbot",
    description="AI-native task management system using Qwen and MCP",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "status": "healthy",
        "service": "phase-iii-chatbot",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Phase III - AI-Powered Todo Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    logger.info(f"Starting server at http://{host}:{port}")
    logger.info("API documentation available at http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )
