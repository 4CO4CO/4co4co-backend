from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.core.exceptions.types import FileSaveError, ValidationError, NotFoundError
from app.core.config.s3 import upload_file_to_s3
from app.core.tasks.panorama_tasks import generate_panorama_task
from app.repositories.lantern_repository import LanternRepository
from app.repositories.music_repository import MusicRepository
from app.repositories.panorama_repository import PanoramaRepository
from app.schemas.db.lanterns import LanternsDBModel
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_response import LanternResponseModel


class LanternService:
    def __init__(self, db):
        self.lantern_repo = LanternRepository(db)
        self.music_repo = MusicRepository(db)
        self.panorama_repo = PanoramaRepository(db)

    async def create_lanterns(self, name, image):
        if not name.strip():
            raise ValidationError("Name is required")

        file_path, original_filename, file_extension, file_size = await self._upload_image_to_s3(image)
        lantern_id = str(uuid4())

        user_model = LanternsDBModel(
            lantern_id=lantern_id,
            user_name=name,
            image_path=file_path,
            original_filename=original_filename,
            file_extension=file_extension,
            file_size=file_size,
            created_at=datetime.utcnow()
        )

        await self.lantern_repo.insert_lantern(user_model.model_dump(exclude={'id'}))

        # Celery 비동기 작업 실행 추가
        generate_panorama_task.delay(prompt=name, lantern_id=lantern_id, image_path=file_path)

        return lantern_id

    def to_lantern_model(self, doc: dict, current_lantern_id: Optional[str]) -> LanternResponseModel:
        return LanternResponseModel(
            lantern_id=doc["lantern_id"],
            owner_name=doc["user_name"],
            is_current_lantern=(doc["lantern_id"] == current_lantern_id)
        )

    async def get_recent_lanterns(self, current_lantern_id: Optional[str] = None, limit: int = 20):
        current_doc = None

        if current_lantern_id:
            current_doc = await self.lantern_repo.find_by_lantern_id(current_lantern_id)
            if not current_doc:
                raise NotFoundError(
                    message=f"Lantern ID {current_lantern_id} not found.",
                    error_code="LANTERN_NOT_FOUND"
                )
            limit -= 1

        other_docs = await self.lantern_repo.find_random_lanterns(
            exclude_lantern_id=current_lantern_id if current_doc else None,
            limit=limit
        )

        docs = [current_doc] + other_docs if current_doc else other_docs

        return [self.to_lantern_model(doc, current_lantern_id) for doc in docs]

    async def get_lantern_detail(self, lantern_id: str, current_lantern_id: str):
        if current_lantern_id:
            count = await self.lantern_repo.count_documents({"lantern_id": current_lantern_id})
            if count == 0:
                raise NotFoundError(f"Current Lantern ID {current_lantern_id} not found.")

        lantern = await self.lantern_repo.find_by_lantern_id(lantern_id)
        if not lantern:
            raise NotFoundError(f"Lantern ID {lantern_id} not found.")

        music = await self.music_repo.find_music_by_lantern_id(lantern_id)
        panorama = await self.panorama_repo.find_panorama_by_lantern_id(lantern_id)

        return LanternDetailResponseModel(
            lantern_id=lantern_id,
            owner_name=lantern["user_name"],
            panorama=panorama["s3_path"] if panorama else "",
            background_sound=music["s3_path"] if music else "",
            is_current_lantern=(lantern_id == current_lantern_id)
        )

    @staticmethod
    async def _upload_image_to_s3(image):
        original_filename = image.filename
        file_extension = original_filename.split('.')[-1]

        try:
            file_path, file_size = await upload_file_to_s3(image, folder="lanterns")
            if file_path is None:
                raise FileSaveError("S3 upload failed")

        except Exception as e:
            raise FileSaveError(f"File upload failed: {e}") from e

        return file_path, original_filename, file_extension, file_size


