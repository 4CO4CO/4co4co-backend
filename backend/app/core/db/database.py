from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for MongoDB.
    - Creates and connects an AsyncIOMotorClient when the app starts
    - Performs a ping test to verify connection
    - Ensures unique index creation on the `lanterns` collection
    - Closes the client when the app shuts down
    """
    global mongo_client
    try:
        logger.info("Creating and connecting MongoDB client...")
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
        )

        # Attach client and DB handle to FastAPI app
        app.mongodb_client = mongo_client
        app.database = mongo_client[settings.MONGO_DB]

        # Connection test (ping)
        await app.database.command("ping")
        logger.info("MongoDB ping successful, connection established")

        # Ensure unique index on lantern_id field
        await app.database["lanterns"].create_index(
            [("lantern_id", 1)],
            unique=True,
            name="unique_lantern_id"
        )
        logger.info("Unique index ensured for lantern_id")

        logger.info("MongoDB lifespan setup completed")
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


def get_mongo_client(request: Request):
    """
    Retrieve the MongoDB database handle from the FastAPI request context.
    Used within FastAPI request handlers.
    """
    return request.app.database


def get_mongo_sync_client():
    """
    Create a synchronous MongoDB client (using PyMongo).
    Useful for contexts like Celery workers that do not support async.
    """
    client = MongoClient(
        settings.MONGO_URI,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
    )
    return client[settings.MONGO_DB]


def get_db():
    """
    Return the synchronous DB object.
    Intended for use in synchronous contexts such as Celery tasks.
    """
    return get_mongo_sync_client()
