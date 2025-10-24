"""
Main entry point for the OdontoLab FastAPI application.

This module configures and creates the FastAPI application with all necessary
middleware, routes, and dependencies for the dental clinic management system.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from app.core.config import settings
from app.application.exceptions import (
    AppError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError
)

# Import API routers
from app.presentation.api.v1.router import api_router

# Settings are imported directly from app.core.config

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="API REST para la gestión de clínicas odontológicas",
        docs_url="/docs",  # Siempre habilitado para Render
        redoc_url="/redoc",  # Siempre habilitado para Render
        openapi_url="/openapi.json"  # Siempre habilitado para Render
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Include API routers
    setup_routes(app)
    
    return app


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup global exception handlers for the application.
    
    Args:
        app (FastAPI): FastAPI application instance
    """
    
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        """Handle custom application errors."""
        status_code = status.HTTP_400_BAD_REQUEST
        
        if isinstance(exc, NotFoundError):
            status_code = status.HTTP_404_NOT_FOUND
        elif isinstance(exc, AuthenticationError):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, AuthorizationError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, ValidationError):
            status_code = status.HTTP_400_BAD_REQUEST
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "type": type(exc).__name__
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": exc.detail,
                    "type": "HTTPException"
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Validation error in request data",
                    "details": exc.errors(),
                    "type": "RequestValidationError"
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "type": "InternalServerError"
                }
            }
        )


def setup_routes(app: FastAPI) -> None:
    """
    Setup API routes for the application.
    
    Args:
        app (FastAPI): FastAPI application instance
    """
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "OdontoLab API",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "environment": settings.ENVIRONMENT
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    # Include API version 1 routes
    app.include_router(api_router, prefix=settings.API_V1_STR)


# Create the application instance
app = create_application()


if __name__ == "__main__":
    """
    Run the application directly.
    
    For development only. In production, use a proper ASGI server like uvicorn.
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )