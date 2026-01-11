from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import asyncio
import traceback
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.api.v1.endpoints import content as content_endpoints
from app.api.v1.endpoints import health as health_endpoints
from app.api.v1.endpoints import sites as sites_endpoints
from app.schemas.content import (
    ErrorPageCreateRequest,
    ErrorPageGetRequest,
    ProtectedPageCreateRequest,
    ProtectedPageGetRequest,
    HcpModalPopupCreateRequest,
    HcpModalPopupGetRequest,
    LoginPageCreateRequest,
    LoginPageGetRequest,
)
from app.schemas.site import DuplicateTemplateRequest, ListPagesRequest

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    setup_logging()
    yield
    # Shutdown
    pass

# Create FastAPI application
app = FastAPI(
    title="WebVerse Content Authoring API",
    description="Backend API for Adobe AEM content authoring and management",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG") == "True" else None,
    redoc_url="/redoc" if os.getenv("DEBUG") == "True" else None,
    lifespan=lifespan
)
# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if os.getenv("DEBUG") == "True" else ["localhost", "127.0.0.1", "*.awsapprunner.com"]
)
# Include API router
API_V1_PREFIX = os.getenv("API_V1_PREFIX") or "/api/v1"
app.include_router(api_router, prefix=API_V1_PREFIX)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "WebVerse Content Authoring API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT")
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        reload=os.getenv("DEBUG") == "True",
        log_level=os.getenv("LOG_LEVEL").lower()
    )

