from fastapi.concurrency import run_in_threadpool
import torch

from app.emotion.main_library import emotion, emotion_to_music_prompt, _MODELS
from app.utils.exceptions import AIServerError
from app.utils.s3 import upload_audio, download_image_from_s3, generate_presigned_url


async def generate_music_pipeline(s3_key: str, duration: int = 10) -> dict:
    """
    Full pipeline for background music generation (서비스 내부에서 직접 처리).
    """
    try:
        # (1) Download image from S3
        image_path = await download_image_from_s3(s3_key)

        # (2) Emotion extraction
        emotion_result = await run_in_threadpool(emotion, image_path, 0.5, 5)
        emotion_label = emotion_result["emotion"]
        caption = emotion_result["caption"]

        # (3) Prompt 생성
        prompt = emotion_to_music_prompt(emotion_label, caption)

        # (4) MusicGen 직접 실행
        processor = _MODELS["music_processor"]
        model = _MODELS["music_model"]
        device = _MODELS["music_device"]

        def _generate():
            inputs = processor(text=[prompt], return_tensors="pt").to(device)
            with torch.no_grad():
                audio_values = model.generate(
                    **inputs,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=1.0,
                    top_k=250,
                    top_p=0.95,
                )
            return audio_values[0, 0].detach().cpu().numpy()

        audio_data = await run_in_threadpool(_generate)
        sample_rate = model.config.audio_encoder.sampling_rate

        # (5) Upload to S3
        audio_s3_key = await upload_audio(audio_data, sample_rate)

        # (6) Presigned URL
        presigned_url = await generate_presigned_url(audio_s3_key, expires_in=3600)

        return {
            "s3_key": audio_s3_key,
            "url": presigned_url,
            "emotion": emotion_label,
            "caption": caption,
            "prompt": prompt,
        }

    except Exception as e:
        raise AIServerError(f"Music generation pipeline failed: {e}")
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
