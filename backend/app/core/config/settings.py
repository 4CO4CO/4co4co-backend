from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "production"

    # MongoDB
    MONGO_URI: str = Field(...)
    MONGO_DB: str = Field(...)
    MONGO_MAX_POOL_SIZE: int = Field(10)
    MONGO_MIN_POOL_SIZE: int = Field(1)
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(30000)

    # API
    API_PREFIX: str = Field(...)
    AI_SERVER_URL: str = Field(...)

    # AWS
    AWS_ACCESS_KEY_ID: str = Field(...)
    AWS_SECRET_ACCESS_KEY: str = Field(...)
    AWS_REGION: str = Field(...)
    AWS_S3_BUCKET_NAME: str = Field(...)

    # Redis
    REDIS_URL: str = Field(...)
    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(...)

    SSE_TIMEOUT: int = Field(180)

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()