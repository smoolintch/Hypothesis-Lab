from fastapi import FastAPI

from app.api.router import api_router
from app.infrastructure.config.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    application.include_router(api_router, prefix="/api")
    return application


app = create_app()
