import io
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.settings import settings


s3_client = boto3.client(
    's3',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


async def upload_file_to_s3(file: UploadFile, folder: str = "uploads"):
    try:
        file_content = await file.read()
        file_size = len(file_content)

        file_extension = file.filename.split('.')[-1]
        s3_file_key = f"{folder}/{uuid4()}.{file_extension}"

        s3_client.upload_fileobj(
            io.BytesIO(file_content),
            settings.AWS_S3_BUCKET_NAME,
            s3_file_key
        )

        file_path = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_file_key}"
        return file_path, file_size

    except ClientError as e:
        print(e)
        return None, 0
