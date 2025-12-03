from typing import List, Optional  # List 추가
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Environment
    APP_ENV: str = Field("production", description="App environment")
    LOG_LEVEL: str = Field("INFO", description="Log level")
    DISCORD_WEBHOOK_URL: Optional[str] = Field(None, description="Discord Webhook URL")

    # MongoDB
    MONGO_URI: str = Field(..., description="MongoDB Connection URI")
    MONGO_DB_NAME: str = Field(..., description="MongoDB Database Name")
    MONGO_MAX_POOL_SIZE: int = Field(10)
    MONGO_MIN_POOL_SIZE: int = Field(0)
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(5000)

    # API
    API_PREFIX: str = Field("/api/v1", description="API Prefix")
    AI_SERVER_URL: str = Field(..., description="AI Server Base URL")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="List of allowed CORS origins"
    )

    # AWS S3
    AWS_ACCESS_KEY_ID: str = Field(...)
    AWS_SECRET_ACCESS_KEY: str = Field(...)
    AWS_REGION: str = Field("ap-northeast-2")
    AWS_S3_BUCKET_NAME: str = Field(...)

    # Celery (Redis)
    CELERY_BROKER_URL: str = Field(..., description="Redis Broker URL")
    CELERY_RESULT_BACKEND: Optional[str] = Field(None, description="Redis Result Backend")

    # SSE
    SSE_TIMEOUT: int = Field(180)
    SSE_POLLING_INTERVAL: int = Field(3)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
