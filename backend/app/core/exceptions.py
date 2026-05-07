from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logging import get_logger

logger = get_logger(__name__)


class SupplyChainGuardianException(Exception):
    """
    Base application exception.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "APPLICATION_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(SupplyChainGuardianException):
    """
    Resource not found exception.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationException(SupplyChainGuardianException):
    """
    Validation failure exception.
    """

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedException(SupplyChainGuardianException):
    """
    Unauthorized access exception.
    """

    def __init__(
        self,
        message: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ExternalServiceException(SupplyChainGuardianException):
    """
    External API/service failure.
    """

    def __init__(
        self,
        message: str = "External service error",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global FastAPI exception handlers.
    """

    @app.exception_handler(SupplyChainGuardianException)
    async def application_exception_handler(
        request: Request,
        exc: SupplyChainGuardianException,
    ):
        logger.error(
            f"{exc.error_code} | {request.method} {request.url} | {exc.message}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ):
        logger.warning(
            f"PYDANTIC_VALIDATION_ERROR | {request.method} {request.url}"
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "PYDANTIC_VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            f"UNHANDLED_EXCEPTION | {request.method} {request.url}"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )