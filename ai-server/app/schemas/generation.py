from pydantic import BaseModel
from app.schemas.common import ResponseModel

class MusicGenerationRequest(BaseModel):
    """
    음악 생성 요청 바디
    """
    image_path: str


class MusicGenerationResult(BaseModel):
    s3_key: str
    emotion: str
    prompt: str
    caption: str


class MusicGenerationResponse(ResponseModel):
    data: MusicGenerationResult