import os
import boto3
from botocore.config import Config
from app.utils.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """
    S3 Client Wrapper for AI Server.
    Provides synchronous methods for downloading and uploading files.
    """

    def __init__(self):
        # 동기 Boto3 클라이언트 생성
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=Config(retries={"max_attempts": 3, "mode": "adaptive"})
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME

    def download_file(self, s3_key: str, local_path: str):
        """
        Download a file from S3 to a local path.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            logger.info(f"[S3 Download] Start: {s3_key} -> {local_path}")
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"[S3 Download] Success")

        except Exception as e:
            logger.error(f"[S3 Download] Failed: {e}")
            raise RuntimeError(f"Failed to download file from S3: {e}")

    def upload_file(self, local_path: str, s3_key: str, content_type: str = "audio/mpeg"):
        """
        Upload a local file to S3.
        """
        try:
            logger.info(f"[S3 Upload] Start: {local_path} -> {s3_key}")
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            logger.info(f"[S3 Upload] Success")

        except Exception as e:
            logger.error(f"[S3 Upload] Failed: {e}")
            raise RuntimeError(f"Failed to upload file to S3: {e}")