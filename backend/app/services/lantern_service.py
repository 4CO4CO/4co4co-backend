import os
from datetime import datetime
from uuid import uuid4

from app.core.exceptions.types import FileSaveError, ValidationError
from app.repositories.lantern_repository import LanternRepository
from app.repositories.music_repository import MusicRepository
from app.repositories.panorama_repository import PanoramaRepository
from app.schemas.db.lantern import LanternDBModel
from app.schemas.response.lantern_detail_response import LanternDetailResponseModel
from app.schemas.response.lantern_list_response import LanternListResponseModel

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class LanternService:
    def __init__(self, db):
        self.lantern_repo = LanternRepository(db)
        self.music_repo = MusicRepository(db)
        self.panorama_repo = PanoramaRepository(db)

    async def create_lanterns(self, name, image):
        if not name.strip():
            raise ValidationError("Name is required")

        file_path, original_filename, file_extension, file_size = await self._save_file(image)
        lantern_id = str(uuid4())

        user_model = LanternDBModel(
            lantern_id=lantern_id,
            user_name=name,
            image_path=file_path,
            original_filename=original_filename,
            file_extension=file_extension,
            file_size=file_size,
            created_at=datetime.utcnow()
        )

        await self.lantern_repo.insert_lantern(user_model.model_dump(exclude={'id'}))
        return lantern_id

    async def get_recent_lanterns(self, current_lantern_id: str, limit: int = 20):
        recent_lanterns = await self.lantern_repo.find_recent_lanterns(limit)
        lanterns = []

        for lantern_doc in recent_lanterns:
            music = await self.music_repo.find_music_by_lantern_id(lantern_doc["lantern_id"])

            lantern = LanternListResponseModel(
                lantern_id=lantern_doc["lantern_id"],
                owner_name=lantern_doc["user_name"],
                emotion=music.get("prompt", "unknown") if music else "unknown",
                is_current_lantern=(lantern_doc["lantern_id"] == current_lantern_id)
            )
            lanterns.append(lantern)

        return lanterns

    async def get_lantern_detail(self, lantern_id: str, current_lantern_id: str):
        lantern = await self.lantern_repo.find_by_lantern_id(lantern_id)
        if not lantern:
            return None

        music = await self.music_repo.find_music_by_lantern_id(lantern_id)
        panorama = await self.panorama_repo.find_panorama_by_lantern_id(lantern_id)

        return LanternDetailResponseModel(
            lantern_id=lantern_id,
            owner_name=lantern["user_name"] if lantern else "Unknown",
            panorama=panorama["s3_path"] if panorama else "",
            background_sound=music["s3_path"] if music else "",
            is_current_lantern=(lantern_id == current_lantern_id)
        )

    @staticmethod
    async def _save_file(image):
        original_filename = image.filename
        file_extension = os.path.splitext(original_filename)[1]
        saved_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        try:
            content = await image.read()
            file_size = len(content)
            await image.seek(0)

            with open(file_path, "wb") as buffer:
                buffer.write(content)
        except Exception as e:
            raise FileSaveError(f"File saving failed: {e}") from e

        return file_path, original_filename, file_extension, file_size
