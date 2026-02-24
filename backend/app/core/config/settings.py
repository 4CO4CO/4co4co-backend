from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Environment
    APP_ENV: str = Field("production", description="Application environment (e.g., production, development)")
    LOG_LEVEL: str = Field("INFO", description="Log level (DEBUG, INFO, WARNING, ERROR)")
    DISCORD_WEBHOOK_URL: str | None = Field(
        None,
        description="Discord Webhook URL for error alerts (optional)"
    )

    # MongoDB configuration
    MONGO_URI: str = Field(..., description="MongoDB connection URI")
    MONGO_DB: str = Field(..., description="MongoDB database name")
    MONGO_MAX_POOL_SIZE: int = Field(10, description="Maximum number of connections in the pool")
    MONGO_MIN_POOL_SIZE: int = Field(0, description="Minimum number of connections in the pool")
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        5000,
        description="Server selection timeout in milliseconds"
    )
    MONGO_INITDB_DATABASE: str = Field(..., description="Database to initialize on startup")

    # API configuration
    API_PREFIX: str = Field(..., description="API prefix (e.g., /api/v1)")
    AI_SERVER_URL: str = Field(..., description="Base URL of the AI server")

    # AWS configuration
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS secret access key")
    AWS_REGION: str = Field(..., description="AWS region")
    AWS_S3_BUCKET_NAME: str = Field(..., description="S3 bucket name")

    # RabbitMQ configuration
    RABBITMQ_URL: str = Field(..., description="RabbitMQ broker URL")
    RABBITMQ_USER: str = Field(..., description="RabbitMQ username")
    RABBITMQ_PASS: str = Field(..., description="RabbitMQ password")

    # Server-Sent Events (SSE) configuration
    SSE_TIMEOUT: int = Field(
        180,
        gt=0,
        description="SSE connection keep-alive time in seconds"
    )
    SSE_POLLING_INTERVAL: int = Field(
        3,
        gt=0,
        description="Interval in seconds for SSE polling"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
