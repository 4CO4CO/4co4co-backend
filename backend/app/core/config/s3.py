import asyncio
import boto3
from typing import Optional, Tuple
from uuid import uuid4

import aioboto3
from botocore.config import Config
from fastapi import UploadFile

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class S3Service:

    def __init__(self):
        self.session = aioboto3.Session()
        self._s3_client = None
        self._client_cm = None
        self._lock = asyncio.Lock()

    async def get_s3_client(self):
        if self._s3_client:
            return self._s3_client
        async with self._lock:
            if self._s3_client is None:
                self._client_cm = self.session.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION,
                    config=Config(retries={"max_attempts": 3, "mode": "adaptive"})
                )
                self._s3_client = await self._client_cm.__aenter__()
                logger.info("[S3Service] Async Client initialized")
        return self._s3_client

    async def close(self):
        if self._client_cm:
            await self._client_cm.__aexit__(None, None, None)
            self._client_cm = None
            self._s3_client = None
            logger.info("[S3Service] Async Client closed")


s3_service = S3Service()


# -----------------------------------------------------------------------------
# [Async] FastAPI용 비동기 업로드
# -----------------------------------------------------------------------------
async def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> Tuple[Optional[str], int]:
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        safe_folder = (folder or "uploads").strip("/")
        ext = file.filename.split(".")[-1] if file.filename else ""
        s3_key = f"{safe_folder}/{uuid4()}{('.' + ext) if ext else ''}"

        s3_client = await s3_service.get_s3_client()

        await s3_client.upload_fileobj(
            file.file,
            settings.AWS_S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
                "Metadata": {"original_filename": file.filename or "unknown"}
            }
        )
        return s3_key, file_size

    except Exception as e:
        logger.error(f"[Async S3 Upload] Failed: {e}")
        return None, 0
    finally:
        file.file.seek(0)


# -----------------------------------------------------------------------------
# [Sync] Celery Task용 동기 업로드
# -----------------------------------------------------------------------------
def upload_file_to_s3_sync(file_data: bytes, filename: str, folder: str = "generated") -> Optional[str]:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        safe_folder = folder.strip("/")
        ext = filename.split(".")[-1] if "." in filename else ""
        s3_key = f"{safe_folder}/{uuid4()}{('.' + ext) if ext else ''}"

        s3_client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_data,
            ContentType="audio/mpeg" if ext == "mp3" else "application/octet-stream"
        )

        logger.info(f"[Sync S3 Upload] Success: {s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"[Sync S3 Upload] Failed: {e}")
        return None


# -----------------------------------------------------------------------------
# Presigned URL (Async)
# -----------------------------------------------------------------------------
async def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> Optional[str]:
    try:
        s3_client = await s3_service.get_s3_client()
        url = await s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        logger.error(f"[Presigned URL] Failed: {e}")
        return None


async def init_s3_service():
    await s3_service.get_s3_client()


async def close_s3_service():
    await s3_service.close()