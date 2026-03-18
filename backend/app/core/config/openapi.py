from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):

    # 캐시된 openai 스키마 반환
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    for path in openapi_schema.get("paths", {}).values():
        for operation in path.values():
            responses = operation.get("responses", {})

            # 디폴트 422 제거
            if "422" in responses:
                del responses["422"]

    # 캐시 업데이트
    app.openapi_schema = openapi_schema
    return app.openapi_schema
