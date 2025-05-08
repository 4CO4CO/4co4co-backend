from app.core.exceptions import DatabaseError


class PanoramaRepository:
    def __init__(self, db):
        self.collection = db.panoramas

    async def find_panorama_by_user_key(self, user_key):
        try:
            return await self.collection.find_one({"user_key": user_key})
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e
