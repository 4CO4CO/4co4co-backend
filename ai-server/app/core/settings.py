from pydantic import Field
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    WIDTH: int = Field(1920, description="Canvas width")
    HEIGHT: int = Field(1080, description="Canvas height")
    DEVICE: str = Field("cuda", description="Computation device")
    PROMPT_SUFFIX: str = Field(", high quality, 4k", description="Prompt suffix")
    RESIZE_OPTION: str = Field("Full", description="Resize option")

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


settings = Settings()
