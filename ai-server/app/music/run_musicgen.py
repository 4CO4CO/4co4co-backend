import os
import re
import tempfile
from uuid import uuid4

import boto3
import torchaudio

from app.core.settings import settings
from audiocraft.models import MusicGen

from app.core.exceptions import AIServerError, GenerationError

# 모델 로딩
model = MusicGen.get_pretrained("facebook/musicgen-small")
model.set_generation_params(duration=10)

# S3 클라이언트
s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def sanitize_filename(prompt: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", prompt)[:30]


def generate_music(prompt: str, duration: int = 10) -> dict:
    model.set_generation_params(duration=duration)

    try:
        wav = model.generate([prompt], progress=False)
    except Exception as e:
        raise GenerationError(f"Music generation failed: {str(e)}")

    tensor = wav[0].cpu()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            torchaudio.save(tmp.name, tensor, sample_rate=model.sample_rate, format="wav")
            tmp_path = tmp.name

        # S3 업로드
        s3_key = f"music/{uuid4()}.wav"
        try:
            s3_client.upload_file(
                Filename=tmp_path,
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=s3_key,
                ExtraArgs={"ContentType": "audio/wav"}
            )
        except Exception as e:
            raise AIServerError(f"S3 upload failed: {str(e)}")

        s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        file_size = os.path.getsize(tmp_path)
        return {"s3_url": s3_url, "file_size": file_size}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)