import os
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.exceptions import AIServerError
from app.core.settings import settings

# S3 클라이언트
s3_client = boto3.client(
    "s3",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


def upload_file_to_s3(local_path: str, folder: str = "music", content_type: str = "audio/wav") -> dict:
    """
    로컬 파일을 S3에 업로드하고 URL과 파일 크기를 반환

    :param local_path: 업로드할 로컬 파일 경로
    :param folder: S3 업로드 폴더
    :param content_type: MIME 타입
    :return: dict(s3_url, file_size)
    """
    s3_key = f"{folder}/{uuid4()}.wav"
    try:
        s3_client.upload_file(
            Filename=local_path,
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key,
            ExtraArgs={"ContentType": content_type}
        )

        s3_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
        file_size = os.path.getsize(local_path)

        return {"s3_url": s3_url, "file_size": file_size}

    except (BotoCoreError, ClientError) as e:
        raise AIServerError(f"S3 upload failed: {str(e)}") from e
    