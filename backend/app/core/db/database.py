from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config.settings import settings
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    try:
        logger.info("MongoDB 클라이언트 생성 및 연결 시도 중...")
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
        )
        app.mongodb_client = mongo_client
        app.database = mongo_client[settings.MONGO_DB]

        # 연결 테스트 (ping)
        await app.database.command("ping")
        logger.info("MongoDB ping 성공, 연결 정상")

        # 유니크 인덱스 생성
        await app.database["lanterns"].create_index(
            [("lantern_id", 1)],
            unique=True,
            name="unique_lantern_id"
        )
        logger.info("lantern_id에 대한 unique index 보장 완료")

        logger.info("MongoDB lifespan setup 완료")
        yield

    except Exception as e:
        logger.exception("MongoDB 연결 실패")
        raise e

    finally:
        try:
            mongo_client.close()
            logger.info("MongoDB 클라이언트 연결 종료")
        except Exception:
            logger.exception("MongoDB 종료 중 에러 발생")


def get_mongo_client(request: Request):
    return request.app.database


def get_mongo_sync_client():
    client = MongoClient(
        settings.MONGO_URI,
        maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
        minPoolSize=settings.MONGO_MIN_POOL_SIZE,
        serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
    )
    return client[settings.MONGO_DB]

def get_db():
    """
    Celery 워커 등 동기 컨텍스트에서 사용할 DB 객체 반환
    """
    return get_mongo_sync_client()

