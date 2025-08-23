import io
from uuid import uuid4
from typing import Optional, Tuple

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()
        self._s3_client = None

    async def get_s3_client(self):
        """S3 클라이언트를 가져오거나 생성"""
        if self._s3_client is None:
            self._s3_client = self.session.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return self._s3_client

    async def close(self):
        """S3 클라이언트 연결 종료"""
        if self._s3_client:
            await self._s3_client.close()
            self._s3_client = None


# 전역 S3 서비스 인스턴스
s3_service = S3Service()


async def upload_file_to_s3(file: UploadFile, folder: str = "uploads") -> Tuple[Optional[str], int]:
    """
    파일을 S3에 비동기로 업로드

    Args:
        file: 업로드할 파일
        folder: S3 내 폴더 경로

    Returns:
        Tuple[Optional[str], int]: (S3 키, 파일 크기) 또는 (None, 0) if 실패
    """
    s3_client = None
    try:
        # 파일 내용 읽기
        file_content = await file.read()
        file_size = len(file_content)

        # 파일 확장자 및 S3 키 생성
        file_extension = ""
        if file.filename and "." in file.filename:
            file_extension = file.filename.split('.')[-1]

        s3_file_key = f"{folder}/{uuid4()}.{file_extension}" if file_extension else f"{folder}/{uuid4()}"

        logger.info(f"[S3 Upload] Start: filename={file.filename}, size={file_size}, key={s3_file_key}")

        # S3 클라이언트 가져오기
        s3_client = await s3_service.get_s3_client()

        # S3에 비동기 업로드
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
        await file.seek(0)


async def delete_file_from_s3(s3_key: str) -> bool:
    """
    S3에서 파일 삭제

    Args:
        s3_key: 삭제할 파일의 S3 키

    Returns:
        bool: 삭제 성공 여부
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
    S3 파일의 임시 URL 생성

    Args:
        s3_key: 파일의 S3 키
        expires_in: URL 만료 시간(초), 기본값 1시간

    Returns:
        Optional[str]: 임시 URL 또는 None if 실패
    """
    try:
        s3_client = await s3_service.get_s3_client()

        url = await s3_client.generate_presigned_url(
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


# FastAPI 앱에서 사용할 라이프사이클 이벤트
async def init_s3_service():
    """S3 서비스 초기화"""
    logger.info("[S3 Service] Initializing...")


async def close_s3_service():
    """S3 서비스 종료"""
    logger.info("[S3 Service] Closing connections...")
    await s3_service.close()