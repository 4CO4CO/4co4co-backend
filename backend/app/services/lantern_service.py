from app.repositories.music_repository import MusicRepository
from app.repositories.user_repository import UserRepository
from app.schemas.lantern_list_response import LanternListResponseModel


class LanternService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.music_repo = MusicRepository(db)

    async def get_recent_lanterns(self, current_user_key: str, limit: int = 20):
        musics = await self.music_repo.find_recent_musics(limit)
        lanterns = []

        for idx, music in enumerate(musics, start=1):
            user = await self.user_repo.find_user_by_key(music["user_key"])

            lantern = LanternListResponseModel(
                id=idx,
                owner_name=user["name"] if user else "Unknown",
                emotion=music.get("prompt", "unknown"),
                is_current_user=(music["user_key"] == current_user_key)
            )
            lanterns.append(lantern)

        return lanterns
