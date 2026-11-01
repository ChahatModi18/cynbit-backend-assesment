import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import SecurityHeadersMiddleware
from app.database.base import Base
from app.database.connection import engine
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.inquiry import router as inquiry_router

# Configure application logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cynbit.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for startup and shutdown hooks.
    Ensures database tables are created if using SQLite local development.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")
    if settings.is_sqlite:
        logger.info("Initializing SQLite tables via Declarative Base metadata...")
        Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """
    FastAPI Application Factory.
    Configures security middleware, CORS, centralized exception handlers,
    and API versioned routers.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "### Cynbit Technologies — Secure Inquiry Management REST API\n\n"
            "Production-grade reference backend demonstrating decoupled REST architecture, "
            "server-side Pydantic validation, bcrypt password hashing, stateless JWT authentication, "
            "and Role-Based Access Control (RBAC).\n\n"
            "Built by **Chahat Modi** (Final-Year B.Tech CSE, JECRC University, Jaipur)."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # 1. Custom Security Headers & Banner Suppression (FIND-004, FIND-005, FIND-006, FIND-007)
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. Restrictive Cross-Origin Resource Sharing (FIND-003)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    # 3. Centralized RFC 7807 Exception Handlers
    register_exception_handlers(app)

    # 4. Versioned API Routers
    app.include_router(health_router, prefix=settings.API_V1_PREFIX)
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
    app.include_router(inquiry_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    def root_redirect():
        """Redirect root requests to interactive Swagger UI documentation."""
        return RedirectResponse(url="/docs")

    return app


# Application entry point for ASGI server (e.g. Uvicorn)
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

