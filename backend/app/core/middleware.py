import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    모든 요청의 처리 시간을 측정하여 로깅하는 미들웨어
    - 성능 모니터링 및 병목 지점 파악용
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 실제 요청 처리 (endpoint 실행)
        response: Response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 응답 헤더에 처리 시간 추가 (X-Process-Time)
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"{request.method} {request.url.path} "
            f"completed in {process_time:.4f}s "
            f"| Status: {response.status_code}"
        )

        if process_time > 10:
            logger.warning(f"SLOW REQUEST DETECTED: {request.method} {request.url.path} took {process_time:.4f}s")

        return response