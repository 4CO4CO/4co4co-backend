from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for MongoDB.
    """
    global mongo_client
    try:
        logger.info("Creating and connecting MongoDB client...")
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
        )

        # Attach client and DB handle to FastAPI app
        app.mongodb_client = mongo_client
        app.database = mongo_client[settings.MONGO_DB]

        # Connection test
        await app.database.command("ping")
        logger.info("MongoDB ping successful, connection established")

        # Ensure index
        await app.database["lanterns"].create_index(
            [("lantern_id", 1)], unique=True, name="unique_lantern_id"
        )
        logger.info("Unique index ensured for lantern_id")

        yield

    except Exception as e:
        logger.exception("MongoDB connection failed")
        raise e

    finally:
        try:
            mongo_client.close()
            logger.info("MongoDB client connection closed")
        except Exception:
            logger.exception("Error occurred while closing MongoDB client")


def get_mongo_sync_client():
    """Create synchronous MongoDB client."""
    client = MongoClient(
        settings.MONGO_URI,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
    )
    return client[settings.MONGO_DB]