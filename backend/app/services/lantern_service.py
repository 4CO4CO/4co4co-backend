import os
from datetime import datetime
from uuid import uuid4

from app.core.exceptions import FileSaveError, ValidationError
from app.repositories.music_repository import MusicRepository
from app.repositories.panorama_repository import PanoramaRepository
from app.repositories.lantern_repository import LanternRepository
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

    async def create_user(self, name, image):
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

    async def get_recent_lanterns(self, current_user_key: str, limit: int = 20):
        musics = await self.music_repo.find_recent_musics(limit)
        lanterns = []

        for idx, music in enumerate(musics, start=1):
            user = await self.lantern_repo.find_by_lantern_id(music["user_key"])

            lantern = LanternListResponseModel(
                id=idx,
                owner_name=user["name"] if user else "Unknown",
                emotion=music.get("prompt", "unknown"),
                is_current_user=(music["user_key"] == current_user_key)
            )
            lanterns.append(lantern)

        return lanterns

    async def get_lantern_detail(self, lantern_id: str):
        music = await self.music_repo.find_music_by_id(lantern_id)
        if not music:
            return None

        user = await self.lantern_repo.find_by_lantern_id(music["user_key"])
        panorama = await self.panorama_repo.find_panorama_by_user_key(music["user_key"])

        return LanternDetailResponseModel(
            id=str(music["_id"]),
            owner_name=user["name"] if user else "Unknown",
            panorama=panorama["s3_path"] if panorama else "",
            background_sound=music["s3_path"] if music else ""
        )

    async def _save_file(self, image):
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
