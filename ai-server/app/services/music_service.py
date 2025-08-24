from fastapi.concurrency import run_in_threadpool

from app.emotion.emotion import extract_emotion
from app.music.model import generate_locked, SAMPLE_RATE
from app.utils.exceptions import AIServerError
from app.utils.s3 import upload_audio, download_image_from_s3, generate_presigned_url


async def generate_music_pipeline(s3_key: str, duration: int = 10) -> dict:
    """
    Full pipeline for background music generation.

    Returns:
        dict: {
            "s3_key": S3 key of the generated audio,
            "url":   Presigned URL for temporary playback
        }
    """
    try:
        # (1) Download image from S3
        image = await download_image_from_s3(s3_key)

        # (2) Emotion extraction (dummy for now)
        emotion_label = await run_in_threadpool(extract_emotion, image)

        # (3) Music generation (GPU, lock protected)
        audio = await run_in_threadpool(
            generate_locked, [emotion_label], duration=duration
        )

        # (4) Upload generated audio to S3
        audio_s3_key = await upload_audio(audio, SAMPLE_RATE)

        # (5) Generate presigned URL
        presigned_url = await generate_presigned_url(audio_s3_key, expires_in=3600)

        return {"s3_key": audio_s3_key, "url": presigned_url}

    except Exception as e:
        raise AIServerError(f"Music generation pipeline failed: {e}")
