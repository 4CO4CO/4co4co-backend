from app.core.exceptions.types import DatabaseError


class MusicRepository:
    def __init__(self, db):
        self.collection = db.music

    async def save_music(self, music_doc):
        try:
            result = await self.collection.insert_one(music_doc)
            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseError(f"Database insert failed: {e}") from e

    async def find_music_by_lantern_id(self, lantern_id: str):
        try:
            return await self.collection.find_one({"lantern_id": lantern_id})
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

