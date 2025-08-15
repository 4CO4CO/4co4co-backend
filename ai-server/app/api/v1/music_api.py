from typing import Dict

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from app.constants.emotions import EmotionEnum
from app.core.exceptions import AIServerError, GenerationError
from app.music.run_musicgen import generate_music

router = APIRouter(tags=["music"])

class GenerateMusicRequest(BaseModel):
    emotion: EmotionEnum

class GenerateMusicResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, str]

@router.post(
    "/generate-music",
    response_model=GenerateMusicResponse,
    summary="Generate background music from an emotion",
)
async def generate_music_api(body: GenerateMusicRequest):
    """
    배경음 생성을 위한 API (감정 기반)
    - 입력: emotion (Enum)
    - 처리: MusicGen 호출 (동기 함수는 threadpool로 실행)
    - 출력: 생성된 오디오의 S3 키
    """
    emotion_value = body.emotion.value.lower()

    try:
        result = await run_in_threadpool(generate_music, emotion_value, 10)

        if not isinstance(result, dict) or not result.get("s3_key"):
            raise GenerationError("Generator returned no s3_key")

        return GenerateMusicResponse(
            status="success",
            message="Music generated successfully",
            data={"s3_key": result["s3_key"]},
        )

    except AIServerError:
        raise
    except Exception as e:
        raise AIServerError(f"Unexpected error during generation: {e}")
