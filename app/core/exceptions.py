import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("cynbit.exceptions")


class APIException(Exception):
    """Base domain exception with RFC 7807 Problem Details attributes."""
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        title: str = "Internal Server Error",
        detail: str = "An unexpected error occurred on the server.",
        type_uri: str = "https://errors.cynbit.in/internal-error",
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(detail)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type_uri = type_uri
        self.errors = errors or []


class ResourceNotFoundException(APIException):
    def __init__(self, detail: str = "Requested resource was not found."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource Not Found",
            detail=detail,
            type_uri="https://errors.cynbit.in/not-found"
        )


class AuthenticationException(APIException):
    def __init__(self, detail: str = "Could not validate credentials."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Authentication Failed",
            detail=detail,
            type_uri="https://errors.cynbit.in/unauthorized"
        )


class PermissionDeniedException(APIException):
    def __init__(self, detail: str = "Insufficient permissions to perform this operation."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission Denied",
            detail=detail,
            type_uri="https://errors.cynbit.in/forbidden"
        )


class BadRequestException(APIException):
    def __init__(self, detail: str = "Invalid request payload or parameters."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Bad Request",
            detail=detail,
            type_uri="https://errors.cynbit.in/bad-request"
        )


class ConflictException(APIException):
    def __init__(self, detail: str = "Resource conflict detected."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Conflict",
            detail=detail,
            type_uri="https://errors.cynbit.in/conflict"
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized RFC 7807 exception handlers with the FastAPI application."""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        content = {
            "type": exc.type_uri,
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
        }
        if exc.errors:
            content["errors"] = exc.errors
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers={"Content-Type": "application/problem+json"}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        formatted_errors = []
        for err in exc.errors():
            loc = [str(x) for x in err.get("loc", []) if x != "body"]
            formatted_errors.append({
                "field": ".".join(loc) if loc else "body",
                "message": err.get("msg", "Invalid input value"),
                "type": err.get("type", "validation_error")
            })

        status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)
        return JSONResponse(
            status_code=status_code,
            content={
                "type": "https://errors.cynbit.in/validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": "One or more fields failed validation. Please review the errors list.",
                "path": str(request.url.path),
                "errors": formatted_errors
            },
            headers={"Content-Type": "application/problem+json"}
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "https://errors.cynbit.in/http-error",
                "title": "HTTP Error",
                "status": exc.status_code,
                "detail": str(exc.detail),
                "path": str(request.url.path),
            },
            headers={"Content-Type": "application/problem+json"}
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception during {request.method} {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "https://errors.cynbit.in/internal-error",
                "title": "Internal Server Error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "An unexpected error occurred. Our engineering team has been notified.",
                "path": str(request.url.path),
            },
            headers={"Content-Type": "application/problem+json"}
        )

