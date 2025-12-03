from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    # ... (기존 설정 유지) ...
    APP_ENV: str = Field("production", description="App Environment")
    LOG_LEVEL: str = Field("INFO", description="Log Level")
    DISCORD_WEBHOOK_URL: str | None = Field(None)

    # AWS
    AWS_ACCESS_KEY_ID: str = Field(..., min_length=16)
    AWS_SECRET_ACCESS_KEY: str = Field(..., min_length=16)
    AWS_REGION: str = Field(..., pattern=r'^[a-z0-9\-]+$')
    AWS_S3_BUCKET_NAME: str = Field(..., min_length=3)

    # [New] AI Model Config
    # 로컬에 모델 파일이 있는 경로 (없으면 HuggingFace에서 다운로드되도록 로직 구현 필요)
    MODEL_PATH: str = Field("models/", description="Directory to store AI models")

    class Config:
        env_file = ".env"
        extra = "ignore" # 모르는 변수가 있어도 에러 안 나게 (유연성)

settings = Settings()