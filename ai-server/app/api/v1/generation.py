import os
import uuid
import logging
from fastapi import APIRouter, HTTPException

from app.schemas.generation import MusicGenerationRequest, MusicGenerationResponse
from app.services.storage import StorageService
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)
router = APIRouter()
storage = StorageService()


@router.post(
    "/generate-music",
    response_model=MusicGenerationResponse,
    summary="Generate background music from an image"
)
def generate_music(body: MusicGenerationRequest):
    """
    [AI Server Endpoint]
    1. S3에서 이미지 다운로드
    2. AI 모델 로드 -> 추론(감정/프롬프트/음악) -> 메모리 해제
    3. 생성된 음악 S3 업로드
    4. 메타데이터(감정, 프롬프트 등)와 함께 응답 반환
    """
    task_id = str(uuid.uuid4())
    local_image_path = f"/tmp/{task_id}_input.jpg"
    local_music_path = f"/tmp/{task_id}_output.mp3"
    s3_output_key = f"generated/{task_id}.mp3"

    try:
        logger.info(f"[{task_id}] Start processing image: {body.image_path}")

        storage.download_file(body.image_path, local_image_path)

        # AI 생성 (Blocking)
        # ai_engine.generate가 이제 dict(emotion, caption, prompt)를 반환함
        metadata = ai_engine.generate(local_image_path, local_music_path)

        storage.upload_file(local_music_path, s3_output_key)

        logger.info(f"[{task_id}] Music generated: {s3_output_key}, Meta: {metadata}")

        return MusicGenerationResponse(
            status="success",
            message="Music generated successfully",
            data={
                "s3_key": s3_output_key,
                "emotion": metadata.get("emotion", "unknown"),
                "prompt": metadata.get("prompt", ""),
                "caption": metadata.get("caption", "")
            }
        )

    except Exception as e:
        logger.error(f"[{task_id}] Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 리소스 정리
        if os.path.exists(local_image_path):
            os.remove(local_image_path)
        if os.path.exists(local_music_path):
            os.remove(local_music_path)

        ai_engine.unload_models()