from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    MONGO_MAX_POOL_SIZE: int
    MONGO_MIN_POOL_SIZE: int
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int

    class Config:
        env_file = ".env"


settings = Settings()

