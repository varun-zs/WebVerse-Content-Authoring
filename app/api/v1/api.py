from fastapi import APIRouter
from app.api.v1.endpoints import content, sites, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
