from fastapi import Request, status
from fastapi.responses import JSONResponse
from .logger import logger

class CognitiveError(Exception):
    """Base class for all cognitive-os exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class EngineProcessingError(CognitiveError):
    """Raised when a cognitive engine fails processing."""
    def __init__(self, message: str, engine_name: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"engine": engine_name, **(details or {})}
        )

async def cognitive_error_handler(request: Request, exc: CognitiveError):
    """Global exception handler for CognitiveErrors."""
    logger.error(
        f"CognitiveError: {exc.message}",
        extra={"status_code": exc.status_code, "details": exc.details, "path": request.url.path}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message, "details": exc.details, "error_code": exc.__class__.__name__}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.exception(f"Unhandled exception: {str(exc)}", extra={"path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal Server Error", "error_code": "InternalError"}
    )
