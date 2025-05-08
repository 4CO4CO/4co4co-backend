from app.core.exceptions.types import DatabaseError


class LanternRepository:
    def __init__(self, db):
        self.collection = db.lantern

    async def insert_lantern(self, user_doc):
        try:
            result = await self.collection.insert_one(user_doc)
            return result
        except Exception as e:
            raise DatabaseError(f"Database insert failed: {e}") from e

    async def find_by_lantern_id(self, lantern_id):
        try:
            user = await self.collection.find_one({"lantern_id": lantern_id})
            return user
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    async def find_recent_lanterns(self, limit: int = 20):
        try:
            cursor = self.collection.find().sort("created_at", -1).limit(limit)
            return [doc async for doc in cursor]
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e