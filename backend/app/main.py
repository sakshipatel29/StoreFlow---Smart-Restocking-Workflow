from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        description=(
            "Authenticated StoreFlow API for SKU-level sales, auditable inventory changes, "
            "explainable reorder recommendations, supplier purchase orders, and safe demo resets."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    @application.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return application


app = create_app()
