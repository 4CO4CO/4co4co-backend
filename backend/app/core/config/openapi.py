from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 모든 path에 대해 422 제거
    for path in openapi_schema.get("paths", {}).values():
        for operation in path.values():
            responses = operation.get("responses", {})
            if "422" in responses:
                del responses["422"]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
