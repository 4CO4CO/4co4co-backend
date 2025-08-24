import asyncio
import io
import soundfile as sf
from PIL import Image
from typing import Optional, Tuple
from uuid import uuid4

import aioboto3
from botocore.config import Config
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from app.utils.logger import get_logger
from app.utils.settings import settings


logger = get_logger(__name__)


class S3Service:
    """
    Lazy singleton-style S3 client manager.
    - First call: opens aioboto3 client context (__aenter__)
    - Subsequent calls: reuse the same client
    - Close: properly calls __aexit__ to release the connection pool
    """

    def __init__(self):
        self.session = aioboto3.Session()
        self._s3_client = None          # actual client object
        self._client_cm = None          # context manager
        self._lock = asyncio.Lock()     # concurrency control

    async def get_s3_client(self):
        """Returns an initialized S3 client (singleton)."""
        if self._s3_client:
            return self._s3_client

        async with self._lock:
            if self._s3_client is None:
                self._client_cm = self.session.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                    config=Config(retries={"max_attempts": 3, "mode": "adaptive"}),
                )
                self._s3_client = await self._client_cm.__aenter__()
                logger.info("[S3Service] S3 client initialized")

        return self._s3_client

    async def close(self):
        """Close the S3 client properly."""
        if self._client_cm:
            await self._client_cm.__aexit__(None, None, None)
            self._client_cm = None
            self._s3_client = None
            logger.info("[S3Service] S3 client closed")


# Global S3 service instance
s3_service = S3Service()


# --------------------
# File Upload / Delete
# --------------------

async def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> Tuple[Optional[str], int]:
    """Upload a file to S3 asynchronously using streaming (memory efficient)."""
    try:
        # 항상 처음부터 읽히도록 보장
        file.file.seek(0, io.SEEK_SET)

        # 파일 사이즈 계산
        try:
            file_obj = file.file
            pos = file_obj.tell()
            file_obj.seek(0, io.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(pos)
        except Exception:
            file_size = 0
            logger.warning(f"[S3 Upload] Failed to calculate file size: {file.filename}")

        # S3 key 생성
        safe_folder = (folder or "uploads").strip("/")
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else ""
        s3_key = f"{safe_folder}/{uuid4()}{('.' + ext) if ext else ''}"

        # 업로드 실행
        s3_client = await s3_service.get_s3_client()
        await s3_client.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
                "Metadata": {
                    "original_filename": file.filename or "unknown",
                    "file_size": str(file_size),
                },
            },
        )
        logger.info(f"[S3 Upload] Success: key={s3_key}")
        return s3_key, file_size

    except Exception as e:
        logger.exception(f"[S3 Upload] Failed: {e}")
        return None, 0

    finally:
        try:
            file.file.seek(0)
        except Exception:
            pass


async def delete_file_from_s3(s3_key: str) -> bool:
    """Delete a file from S3."""
    try:
        s3_client = await s3_service.get_s3_client()
        await s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=s3_key)
        logger.info(f"[S3 Delete] Success: key={s3_key}")
        return True
    except Exception as e:
        logger.exception(f"[S3 Delete] Failed: key={s3_key}, error={e}")
        return False


# --------------------
# File Download
# --------------------

async def download_image_from_s3(s3_key: str) -> Image.Image:
    """Download an image from S3 and return it as a PIL Image."""
    try:
        s3_client = await s3_service.get_s3_client()
        obj = await s3_client.get_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=s3_key)
        body = await obj["Body"].read()
        return Image.open(io.BytesIO(body)).convert("RGB")
    except Exception as e:
        logger.exception(f"[S3 Download] Failed: key={s3_key}, error={e}")
        raise


async def upload_audio(audio_tensor, sample_rate: int, folder: str = "audios") -> str:
    """Upload generated audio to S3 as WAV and return the S3 key."""
    try:
        audio_np = audio_tensor.squeeze().cpu().numpy() if hasattr(audio_tensor, "cpu") else audio_tensor
        buf = io.BytesIO()
        sf.write(buf, audio_np, sample_rate, format="WAV")
        buf.seek(0)

        s3_key = f"{folder}/{uuid4()}.wav"
        s3_client = await s3_service.get_s3_client()
        await s3_client.upload_fileobj(
            buf,
            settings.AWS_S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": "audio/wav"},
        )
        logger.info(f"[S3 Audio Upload] Success: key={s3_key}")
        return s3_key
    except Exception as e:
        logger.exception(f"[S3 Audio Upload] Failed: {e}")
        raise


# --------------------
# Presigned URL
# --------------------

async def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> Optional[str]:
    """Generate a presigned URL for GET request."""
    try:
        s3_client = await s3_service.get_s3_client()

        if asyncio.iscoroutinefunction(s3_client.generate_presigned_url):
            url = await s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": s3_key},
                ExpiresIn=expires_in,
            )
        else:
            url = await run_in_threadpool(
                s3_client.generate_presigned_url,
                "get_object",
                Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": s3_key},
                ExpiresIn=expires_in,
            )

        logger.info(f"[S3 Presigned URL] Generated: key={s3_key}, expires_in={expires_in}")
        return url
    except Exception as e:
        logger.exception(f"[S3 Presigned URL] Failed: {e}")
        return None