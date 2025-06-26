from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    AWS_ACCESS_KEY_ID: str = Field(
        ..., min_length=16, max_length=128, description="AWS Access Key ID"
    )
    AWS_SECRET_ACCESS_KEY: str = Field(
        ..., min_length=16, description="AWS Secret Access Key"
    )
    AWS_REGION: str = Field(
        ..., pattern=r'^[a-z0-9\-]+$', description="AWS Region (e.g., ap-northeast-2)"
    )
    AWS_S3_BUCKET_NAME: str = Field(
        ..., min_length=3, max_length=63, description="S3 Bucket Name"
    )

    class Config:
        env_file = ".env"
        extra = "forbid"


settings = Settings()
