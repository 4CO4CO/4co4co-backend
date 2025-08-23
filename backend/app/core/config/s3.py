import io
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION
)


async def upload_file_to_s3(file: UploadFile, folder: str = "uploads"):
    try:
        file_content = await file.read()
        file_size = len(file_content)

        file_extension = file.filename.split('.')[-1]
        s3_file_key = f"{folder}/{uuid4()}.{file_extension}"

        logger.info(f"[S3 Upload] Start: filename={file.filename}, size={file_size}, key={s3_file_key}")

        s3_client.upload_fileobj(
            io.BytesIO(file_content),
            settings.AWS_S3_BUCKET_NAME,
            s3_file_key
        )

        logger.info(f"[S3 Upload] Success: key={s3_file_key}, bucket={settings.AWS_S3_BUCKET_NAME}")
        return s3_file_key, file_size

    except ClientError as e:
        logger.exception(f"[S3 Upload] Failed: filename={file.filename}, bucket={settings.AWS_S3_BUCKET_NAME}")
        return None, 0
