from app.core.exceptions import DatabaseError


class MusicRepository:
    def __init__(self, db):
        self.collection = db.music

    async def save_user_music(self, user_key: str, prompt: str, s3_path: str, created_at):
        music_doc = {
            "user_key": user_key,
            "prompt": prompt,
            "s3_path": s3_path,
            "created_at": created_at
        }
        try:
            result = await self.collection.insert_one(music_doc)
            return str(result.inserted_id)
        except Exception as e:
            raise DatabaseError(f"Database insert failed: {e}") from e

    async def find_music_by_user_key(self, user_key: str, limit: int = 10):
        try:
            cursor = self.collection.find({"user_key": user_key}).sort("created_at", -1).limit(limit)
            return [doc async for doc in cursor]
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e
