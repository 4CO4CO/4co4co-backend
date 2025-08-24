from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 환경
    APP_ENV: str = Field("production")
    LOG_LEVEL: str = Field("INFO", description="로그 레벨 (DEBUG, INFO, WARNING, ERROR)")
    DISCORD_WEBHOOK_URL: str | None = Field(None, description="Discord Webhook URL for error alerts")

    # MongoDB
    MONGO_URI: str = Field(...)
    MONGO_DB: str = Field(...)
    MONGO_MAX_POOL_SIZE: int = Field(10)
    MONGO_MIN_POOL_SIZE: int = Field(0)
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(5000)
    MONGO_INITDB_DATABASE: str = Field(...)

    # API
    API_PREFIX: str = Field(...)
    AI_SERVER_URL: str = Field(...)

    # AWS
    AWS_ACCESS_KEY_ID: str = Field(...)
    AWS_SECRET_ACCESS_KEY: str = Field(...)
    AWS_REGION: str = Field(...)
    AWS_S3_BUCKET_NAME: str = Field(...)

    # RABBITMQ
    RABBITMQ_URL: str = Field(...)
    RABBITMQ_USER: str = Field(...)
    RABBITMQ_PASS: str = Field(...)

    # SSE
    SSE_TIMEOUT: int = Field(180, gt=0, description="SSE 연결 유지 시간 (초)")
    SSE_POLLING_INTERVAL: int = Field(3, gt=0, description="SSE 폴링 간격 (초)")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
