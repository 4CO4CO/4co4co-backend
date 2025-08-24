import asyncio
import io
from typing import Optional, Tuple
from uuid import uuid4

import aioboto3
from botocore.config import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

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
        """
        Returns an initialized S3 client.
        Creates and enters the client context on the first call.
        """
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
                # Enter the context manager → initialize the connection pool
                self._s3_client = await self._client_cm.__aenter__()

                logger.info("[S3Service] S3 client initialized")

        return self._s3_client

    async def close(self):
        """
        Properly closes the S3 client by exiting the context manager.
        """
        if self._client_cm:
            await self._client_cm.__aexit__(None, None, None)
            self._client_cm = None
            self._s3_client = None
            logger.info("[S3Service] S3 client closed")


# Global S3 service instance
s3_service = S3Service()


async def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> Tuple[Optional[str], int]:
    """
    Upload a file to S3 asynchronously.

    Args:
        file: The file to be uploaded
        folder: Folder path inside S3

    Returns:
        Tuple[Optional[str], int]: (S3 key, file size) or (None, 0) if failed
    """
    s3_client = None
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Extract file extension and generate S3 key
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = file.filename.split('.')[-1]

        s3_file_key = f"{folder}/{uuid4()}.{file_extension}" if file_extension else f"{folder}/{uuid4()}"

        logger.info(f"[S3 Upload] Start: filename={file.filename}, size={file_size}, key={s3_file_key}")

        # Get S3 client
        s3_client = await s3_service.get_s3_client()

        # Upload to S3 asynchronously
        await s3_client.upload_fileobj(
            io.BytesIO(file_content),
            settings.AWS_S3_BUCKET_NAME,
            s3_file_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream",
                "Metadata": {
                    "original_filename": file.filename or "unknown",
                    "file_size": str(file_size)
                }
            }
        )

        logger.info(f"[S3 Upload] Success: key={s3_file_key}, bucket={settings.AWS_S3_BUCKET_NAME}")
        return s3_file_key, file_size

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"[S3 Upload] AWS Error: filename={file.filename}, error_code={error_code}, error={str(e)}")
        return None, 0

    except Exception as e:
        logger.exception(f"[S3 Upload] Unexpected Error: filename={file.filename}, error={str(e)}")
        return None, 0

    finally:
        # Reset file pointer for possible reuse
        await file.seek(0)


async def delete_file_from_s3(s3_key: str) -> bool:
    """
    Delete a file from S3.

    Args:
        s3_key: S3 key of the file to be deleted

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        s3_client = await s3_service.get_s3_client()

        await s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key
        )

        logger.info(f"[S3 Delete] Success: key={s3_key}, bucket={settings.AWS_S3_BUCKET_NAME}")
        return True

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"[S3 Delete] AWS Error: key={s3_key}, error_code={error_code}, error={str(e)}")
        return False

    except Exception as e:
        logger.exception(f"[S3 Delete] Unexpected Error: key={s3_key}, error={str(e)}")
        return False


async def get_file_url_from_s3(s3_key: str, expires_in: int = 3600) -> Optional[str]:
    """
    Generate a temporary pre-signed URL for an S3 file.

    Args:
        s3_key: S3 key of the file
        expires_in: Expiration time of the URL in seconds (default: 1 hour)

    Returns:
        Optional[str]: Temporary URL or None if failed
    """
    try:
        s3_client = await s3_service.get_s3_client()

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_S3_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expires_in
        )

        logger.info(f"[S3 URL] Generated: key={s3_key}, expires_in={expires_in}")
        return url

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"[S3 URL] AWS Error: key={s3_key}, error_code={error_code}, error={str(e)}")
        return None

    except Exception as e:
        logger.exception(f"[S3 URL] Unexpected Error: key={s3_key}, error={str(e)}")
        return None


# Lifecycle events for FastAPI app
async def init_s3_service():
    """Initialize S3 service"""
    logger.info("[S3 Service] Initializing...")


async def close_s3_service():
    """Shutdown S3 service and close connections"""
    logger.info("[S3 Service] Closing connections...")
    await s3_service.close()
