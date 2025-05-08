from app.core.exceptions.types import DatabaseError


class PanoramaRepository:
    def __init__(self, db):
        self.collection = db.panorama

    async def find_panorama_by_lantern_id(self, lantern_id):
        try:
            return await self.collection.find_one({"lantern_id": lantern_id})
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e
