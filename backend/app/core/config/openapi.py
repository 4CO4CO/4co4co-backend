from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):

    # the cached version
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
            # remove default 422 response (validation errors)
            if "422" in responses:
                del responses["422"]

    # cache the modified schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema
