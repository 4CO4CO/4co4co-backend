from app.core.exceptions import DatabaseError


class UserRepository:
    def __init__(self, db):
        self.collection = db.users

    async def insert_user(self, user_doc):
        try:
            result = await self.collection.insert_one(user_doc)
            return result
        except Exception as e:
            raise DatabaseError(f"Database insert failed: {e}") from e

    async def find_user_by_key(self, user_key):
        try:
            user = await self.collection.find_one({"user_key": user_key})
            return user
        except Exception as e:
            raise DatabaseError(f"Database query failed: {e}") from e
