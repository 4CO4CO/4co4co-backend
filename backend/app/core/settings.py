from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str = Field(..., description="MongoDB connection URI")
    MONGO_DB: str = Field(..., description="MongoDB database name")
    MONGO_MAX_POOL_SIZE: int = Field(10, description="Maximum number of connections in the pool")
    MONGO_MIN_POOL_SIZE: int = Field(1, description="Minimum number of connections in the pool")
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(30000, description="Server selection timeout in milliseconds")

    API_PREFIX: str = Field("/api/v1", description="Base API prefix")

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


settings = Settings()

