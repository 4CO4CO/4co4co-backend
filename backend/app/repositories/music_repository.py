from bson import ObjectId
from app.core.exceptions import DatabaseError


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

    async def find_recent_musics(self, limit: int = 20):
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            return [doc async for doc in cursor]
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_music_by_id(self, music_id: str):
        try:
            return await self.collection.find_one({"_id": ObjectId(music_id)})
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e
