from fastapi.concurrency import run_in_threadpool
from app.music.emotion import extract_emotion
from app.music.model import generate_locked, SAMPLE_RATE
from app.utils.s3 import upload_audio, download_image_from_s3


async def generate_music_pipeline(s3_key: str, duration: int = 10) -> str:
    """
    Full pipeline for background music generation.
    1. Extract emotion from image (CPU) - currently dummy
    2. Generate music with MusicGen (GPU, lock protected)
    3. Upload result to S3
    """
    # 1) Download image
    image = await download_image_from_s3(s3_key)

    # 2) Emotion extraction (dummy)
    emotion_label = await run_in_threadpool(extract_emotion, image)

    # 3) Generate music
    audio = await run_in_threadpool(generate_locked, [emotion_label], duration=duration)

    # 4) Upload audio to S3
    audio_s3_key = await upload_audio(audio, SAMPLE_RATE)

    return audio_s3_key
