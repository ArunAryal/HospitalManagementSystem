"""
Application middleware for request/response handling and error processing.

This module provides middleware for consistent error handling, request logging,
and response formatting across the entire API.
"""

import time
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.exceptions import BaseAPIException
from backend.logging_config import RequestLogger, logger


async def exception_handler_middleware(
    request: Request, call_next: Callable
) -> Response:
    """
    Middleware to handle exceptions globally.

    This middleware catches all exceptions and converts them to appropriate
    HTTP responses with consistent error formatting.
    """
    try:
        response = await call_next(request)
        return response
    except BaseAPIException as e:
        logger.warning(f"API Exception: {e.message}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "error": e.to_dict(),
            },
        )
    except RequestValidationError as e:
        logger.warning(f"Validation Error: {str(e)}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "error_code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": {"errors": e.errors()},
                },
            },
        )
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)}
                    if not isinstance(e, BaseAPIException)
                    else {},
                },
            },
        )


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to log all HTTP requests and responses.

    Logs request/response details including method, path, status code, and duration.
    """
    start_time = time.time()

    # Log request
    RequestLogger.log_request(
        method=request.method,
        path=request.url.path,
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    RequestLogger.log_response(
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response


async def cors_middleware_wrapper(request: Request, call_next: Callable) -> Response:
    """
    Wrapper middleware for CORS handling.

    Ensures proper CORS headers are set on all responses.
    """
    if request.method == "OPTIONS":
        return Response(
            content="OK",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


class RequestContextMiddleware:
    """
    Middleware to add request context information.

    This can be extended to include user information from JWT tokens, etc.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Add request ID to headers
        request_id = str(time.time())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: dict = None,
) -> dict:
    """
    Create a standardized error response.

    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        Dictionary with error response structure
    """
    return {
        "success": False,
        "error": {
            "error_code": error_code,
            "message": message,
            "details": details or {},
        },
    }


def create_success_response(data: Any = None, message: str = "Success") -> dict:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Success message

    Returns:
        Dictionary with success response structure
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }
