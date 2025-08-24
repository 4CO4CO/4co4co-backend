from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    """
    Generate a custom OpenAPI schema for the FastAPI app.
    - Uses FastAPI's built-in get_openapi() to build the schema
    - Removes the default 422 validation error response from all paths
    """

    # If schema already generated, return the cached version
    if app.openapi_schema:
        return app.openapi_schema

    # Generate default OpenAPI schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Iterate through all paths and operations
    for path in openapi_schema.get("paths", {}).values():
        for operation in path.values():
            responses = operation.get("responses", {})
            # Remove default 422 response (validation errors)
            if "422" in responses:
                del responses["422"]

    # Cache the modified schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema
