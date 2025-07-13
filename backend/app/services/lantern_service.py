import random
from datetime import datetime
from typing import Optional, List

from fastapi import UploadFile

from app.core.config.s3 import upload_file_to_s3
from app.core.exceptions.types import FileSaveError, NotFoundError, ForbiddenError, ValidationError
from app.repositories.lantern_repository import LanternRepository
from app.schemas.db.lantern import LanternDBModel, ImageInfo, MusicStatusInfo
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel
from app.core.tasks.music_tasks import process_lantern_music


def to_lantern_model(doc: dict, current_lantern_id: Optional[str]) -> LanternResponseModel:
    return LanternResponseModel(
        lantern_id=doc["lantern_id"],
        owner_name=doc["user_name"],
        is_current_lantern=(doc["lantern_id"] == current_lantern_id)
    )


class LanternService:
    def __init__(self, db):
        self.lantern_repo = LanternRepository(db)

    """
    랜턴 생성
    """
    async def create_lanterns(
            self,
            name: str,
            images: List[UploadFile],
            is_public: bool = True
    ) -> str:
        # 1) 랜턴 ID 생성
        MAX_RETRY = 5
        for _ in range(MAX_RETRY):
            code = str(random.randint(1000, 9999))
            lantern_id = f"{name}-{code}"
            if not await self.lantern_repo.exists_by_lantern_id(lantern_id):
                break
        else:
            raise ValidationError("Duplicate lantern ID")

        # 2) 이미지 S3 업로드
        uploaded_images: List[ImageInfo] = []
        for img in images:
            path, orig, ext, size = await self._upload_image_to_s3(img)
            uploaded_images.append(
                ImageInfo(
                    s3_path=path,
                    original_filename=orig,
                    file_extension=ext,
                    file_size=size
                )
            )

        # 3) Celery 태스크 등록 및 상태 정보 구성
        task_ids: List[str] = []
        music_statuses: List[MusicStatusInfo] = []
        for info in uploaded_images:
            task = process_lantern_music.delay(
                lantern_id,
                info.s3_path,
            )
            task_ids.append(task.id)

            music_statuses.append(
                MusicStatusInfo(
                    image_s3=info.s3_path,
                    task_id=task.id,
                    status="pending",
                    s3_key=None
                )
            )

        # 4) 기본 랜턴 문서 삽입
        lantern_doc = LanternDBModel(
            lantern_id=lantern_id,
            user_name=name,
            images=uploaded_images,
            musics=[],
            music_tasks=task_ids,
            music_statuses=music_statuses,
            is_public=is_public,
            created_at=datetime.utcnow()
        )
        await self.lantern_repo.insert_lantern(lantern_doc.model_dump(exclude={'id'}))

        # 5) 클라이언트에는 lantern_id만 반환
        return lantern_id

    """
    최근 랜턴 조회 (최신 랜턴 + 랜덤 추천 조합)
    """

    async def get_recent_lanterns(self, current_lantern_id: Optional[str] = None, limit: int = 20):
        current_doc = None

        # 현재 선택된 랜턴 ID가 존재하면 먼저 조회
        if current_lantern_id:
            current_doc = await self.lantern_repo.find_by_lantern_id(current_lantern_id)
            if not current_doc:
                raise NotFoundError(
                    message=f"Lantern ID {current_lantern_id} not found.",
                    error_code="LANTERN_NOT_FOUND"
                )
            limit -= 1  # 나머지 추천 수 조정

        # 나머지 랜덤 랜턴 목록 조회
        other_docs = await self.lantern_repo.find_random_lanterns(
            exclude_lantern_id=current_lantern_id if current_doc else None,
            limit=limit
        )

        docs = [current_doc] + other_docs if current_doc else other_docs

        # 응답 모델 리스트 반환
        return [to_lantern_model(doc, current_lantern_id) for doc in docs]

    """
    특정 랜턴 상세 조회
    """

    async def get_lantern_detail(self, lantern_id: str):
        # 랜턴 ID로 문서 조회
        lantern = await self.lantern_repo.find_by_lantern_id(lantern_id)
        if not lantern:
            raise NotFoundError(
                message=f"Lantern ID {lantern_id} not found.",
                error_code="LANTERN_NOT_FOUND"
            )

        # 비공개 랜턴일 경우 접근 금지
        if not lantern.get("is_public", False):
            raise ForbiddenError(
                message="This lantern is private.",
                error_code="LANTERN_NOT_PUBLIC"
            )

        # 이미지 경로 리스트 추출
        image_paths = [
            image["s3_path"] for image in lantern.get("images", []) if "s3_path" in image
        ]

        # 배경음악 경로 리스트 추출
        background_sounds = [
            music["s3_path"] for music in lantern.get("musics", []) if "s3_path" in music
        ]

        # 상세 응답 모델 반환
        return LanternDetailResponseModel(
            lantern_id=lantern["lantern_id"],
            owner_name=lantern["user_name"],
            images=image_paths,
            background_sounds=background_sounds
        )

    """
    S3에 이미지 업로드 후 파일 정보 반환
    """

    @staticmethod
    async def _upload_image_to_s3(image):
        original_filename = image.filename
        file_extension = original_filename.split('.')[-1]

        try:
            s3_key, file_size = await upload_file_to_s3(image, folder="lanterns")
            if s3_key is None:
                raise FileSaveError("S3 upload failed")

        except Exception as e:
            raise FileSaveError(f"File upload failed: {e}") from e

        return s3_key, original_filename, file_extension, file_size
