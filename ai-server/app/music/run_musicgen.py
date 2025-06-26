import os
import re
import tempfile
from uuid import uuid4

import boto3
import torchaudio

from app.core.settings import settings
from audiocraft.models import MusicGen

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
    wav = model.generate([prompt], progress=False)
    tensor = wav[0].cpu()

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            torchaudio.save(tmp.name, tensor, sample_rate=model.sample_rate, format="wav")
            tmp_path = tmp.name  # 저장된 경로

        # S3 업로드
        s3_key = f"music/{uuid4()}.wav"
        s3_client.upload_file(
            Filename=tmp_path,
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key,
            ExtraArgs={"ContentType": "audio/wav"}
        )

        s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        file_size = os.path.getsize(tmp_path)

        return {"s3_url": s3_url, "file_size": file_size}

    except Exception as e:
        print("S3 업로드 실패:", e)
        return {"s3_url": None, "file_size": 0}

    finally:
        # 파일 삭제
        if os.path.exists(tmp_path):
            os.remove(tmp_path)