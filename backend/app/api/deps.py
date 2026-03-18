from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.db.dependencies import get_db
from app.services.lantern_service import LanternService


def get_lantern_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> LanternService:
    """
    Dependency to provide a LanternService instance with an async DB session.
    """
    return LanternService(db)