"""
API Routers Package.
"""
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.inquiry import router as inquiry_router

__all__ = ["health_router", "auth_router", "inquiry_router"]

