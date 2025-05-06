from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.settings import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # MongoDB 비동기 클라이언트 생성 (풀 사이즈 및 타임아웃 조정)
        mongo_client = AsyncIOMotorClient(
            settings.MONGO_URI,
            maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
            minPoolSize=settings.MONGO_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS
        )
        app.mongodb_client = mongo_client
        app.database = mongo_client[settings.MONGO_DB]
        logger.info("MongoDB 클라이언트 생성 및 연결 시도 중...")

        # 연결 테스트 (ping)
        await app.database.command("ping")
        logger.info("MongoDB ping 성공, 연결 정상")

        yield  # FastAPI 앱 실행됨

    except Exception as e:
        logger.error(f"MongoDB 연결 실패: {e}")
        raise e

    finally:
        try:
            mongo_client.close()
            logger.info("MongoDB 클라이언트 연결 종료")
        except Exception as close_err:
            logger.error(f"MongoDB 종료 중 에러 발생: {close_err}")


def get_mongo_client(request: Request):
    return request.app.database