from fastapi import FastAPI
from app.core.db.database import lifespan
from app.core.config.cors import setup_cors
from app.core.config.settings import settings
from app.core.exceptions import setup_exception_handlers
from app.api.v1.routers import api_router
from app.core.config.openapi import custom_openapi


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # CORS 설정
    setup_cors(app)

    # 라우터 등록
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # 예외 핸들러 등록
    setup_exception_handlers(app)

    # OpenAPI 문서 커스터마이징
    app.openapi = lambda: custom_openapi(app)

    return app
