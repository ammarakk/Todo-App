"""
Application Configuration using Pydantic Settings
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "todo-backend"
    app_version: str = "5.0.0"
    app_env: str = "local"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:secretpass@localhost:5432/todo"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "todo"
    database_user: str = "postgres"
    database_password: str = "secretpass"
    
    # Dapr
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    dapr_host: str = "localhost"
    
    # Kafka (via Dapr)
    kafka_brokers: str = "redpanda:9092"
    kafka_topic_task_events: str = "task-events"
    kafka_topic_reminders: str = "reminders"
    kafka_topic_task_updates: str = "task-updates"
    kafka_topic_audit_events: str = "audit-events"
    
    # AI (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    ai_max_tokens: int = 500
    ai_temperature: float = 0.7
    
    # Security
    jwt_secret: str = "development-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    log_level: str = "INFO"
    correlation_id_header: str = "X-Correlation-ID"
    
    # Neon Database (Production Override)
    @property
    def neon_database_url(self) -> str:
        """Neon production database URL"""
        return "postgresql+asyncpg://neondb_owner:npg_4oK0utXaHpci@ep-broad-darkness-abnsobdy-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
