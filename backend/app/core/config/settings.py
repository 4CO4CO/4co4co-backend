from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB 설정
    MONGO_URI: str = Field(..., description="MongoDB connection URI")
    MONGO_DB: str = Field(..., description="MongoDB database name")
    MONGO_MAX_POOL_SIZE: int = Field(10, description="Maximum number of connections in the pool")
    MONGO_MIN_POOL_SIZE: int = Field(1, description="Minimum number of connections in the pool")
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(30000, description="Server selection timeout in milliseconds")

    # API 설정
    API_PREFIX: str = Field("/api/v1", description="Base API prefix")
    USE_MOCK: bool = Field(True, description="Use mock mode for testing AI server requests")

    # AWS S3 설정 추가
    AWS_ACCESS_KEY_ID: str = Field(..., description="AWS Access Key ID for S3")
    AWS_SECRET_ACCESS_KEY: str = Field(..., description="AWS Secret Access Key for S3")
    AWS_REGION: str = Field("ap-northeast-2", description="AWS Region for S3")
    AWS_S3_BUCKET_NAME: str = Field(..., description="AWS S3 Bucket Name")

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


settings = Settings()
