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
    allowed_hosts=["*"] if os.getenv("DEBUG") == "True" else ["localhost", "127.0.0.1"]
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

def get_app(payload: dict) -> dict:
    """
    Main routing function that directs requests to appropriate handlers.
    
    Args:
        payload: Dictionary containing 'endpoint' and 'request_body'
                 Example: {"endpoint": "duplicate-template", "request_body": {...}}
        
    Returns:
        dict: Response from the handler function in Domino format
    """
    try:
        endpoint = payload.get("endpoint", "").strip().lstrip("/")
        request_body = payload.get("request_body", {})
        
        # Route to appropriate function
        if endpoint == "duplicate-template":
            return invoke_duplicate_template(request_body)
        elif endpoint == "list-pages":
            return invoke_list_pages(request_body)
        elif endpoint == "health":
            return invoke_health_check(request_body)
        elif endpoint == "aem":
            return invoke_aem_health(request_body)
        elif endpoint == "create-error-pages":
            return invoke_create_error_pages(request_body)
        elif endpoint == "error-pages":
            return invoke_get_error_pages(request_body)
        elif endpoint == "protected-page":
            return invoke_create_protected_page(request_body)
        elif endpoint == "get-protected-page":
            return invoke_get_protected_page(request_body)
        elif endpoint == "create-hcp-modal-popup":
            return invoke_create_hcp_modal_popup(request_body)
        elif endpoint == "hcp-modal-popup":
            return invoke_get_hcp_modal_popup(request_body)
        elif endpoint == "create-login-page":
            return invoke_create_login_page(request_body)
        elif endpoint == "login-page":
            return invoke_get_login_page(request_body)
        else:
            return {
                "data": {
                    "error": f"Unknown endpoint: {endpoint}",
                    "available_endpoints": [
                        "duplicate-template", "list-pages", "health", "aem",
                        "create-error-pages", "error-pages", "protected-page", "get-protected-page",
                        "create-hcp-modal-popup", "hcp-modal-popup", "create-login-page", "login-page"
                    ]
                },
                "model_time_ms": 0,
                "timing": 0.0
            }
            
    except Exception as e:
        return {
            "data": {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            },
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_duplicate_template(payload: dict) -> dict:
    """
    Directly invoke the duplicate template function without going through the endpoint.
    
    Args:
        payload: Dictionary containing market_region and source_path
                 Example: {"market_region": "india", "source_path": "/content/..."}
        
    Returns:
        dict: Result from duplicate_empty_template function wrapped in Domino format
    """
    try:
        # Extract fields from payload
        market_region = payload.get("market_region")
        source_path = payload.get("source_path")
        
        # Create request object
        request = DuplicateTemplateRequest(
            market_region=market_region,
            source_path=source_path
        )
        
        # Directly call the handler function using asyncio.run
        result = asyncio.run(sites_endpoints.duplicate_empty_template(request))
        
        # Convert to dict if it's a Pydantic model
        response_data = None
        if hasattr(result, "model_dump"):
            response_data = result.model_dump()
        elif hasattr(result, "dict"):
            response_data = result.dict()
        else:
            response_data = result
        
        # Wrap in Domino format like test_endpoint
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
            
    except Exception as e:
        return {
            "data": {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            },
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_list_pages(payload: dict) -> dict:
    """Invoke list pages endpoint"""
    try:
        request = ListPagesRequest(**payload) if payload else None
        result = asyncio.run(sites_endpoints.list_pages(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_health_check(payload: dict) -> dict:
    """Invoke health check endpoint"""
    try:
        result = asyncio.run(health_endpoints.health_check())
        return {
            "data": result,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_aem_health(payload: dict) -> dict:
    """Invoke AEM health check endpoint"""
    try:
        result = asyncio.run(health_endpoints.aem_health())
        return {
            "data": result,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_create_error_pages(payload: dict) -> dict:
    """Invoke create error pages endpoint"""
    try:
        request = ErrorPageCreateRequest(**payload)
        result = asyncio.run(content_endpoints.create_error_pages(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_get_error_pages(payload: dict) -> dict:
    """Invoke get error pages endpoint"""
    try:
        request = ErrorPageGetRequest(**payload)
        result = asyncio.run(content_endpoints.get_error_pages(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_create_protected_page(payload: dict) -> dict:
    """Invoke create protected page endpoint"""
    try:
        request = ProtectedPageCreateRequest(**payload)
        result = asyncio.run(content_endpoints.create_protected_page(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_get_protected_page(payload: dict) -> dict:
    """Invoke get protected page endpoint"""
    try:
        request = ProtectedPageGetRequest(**payload)
        result = asyncio.run(content_endpoints.get_protected_page(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_create_hcp_modal_popup(payload: dict) -> dict:
    """Invoke create HCP modal popup endpoint"""
    try:
        request = HcpModalPopupCreateRequest(**payload)
        result = asyncio.run(content_endpoints.create_hcp_modal_popup_endpoint(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_get_hcp_modal_popup(payload: dict) -> dict:
    """Invoke get HCP modal popup endpoint"""
    try:
        request = HcpModalPopupGetRequest(**payload)
        result = asyncio.run(content_endpoints.get_hcp_modal_popup(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_create_login_page(payload: dict) -> dict:
    """Invoke create login page endpoint"""
    try:
        request = LoginPageCreateRequest(**payload)
        result = asyncio.run(content_endpoints.create_login_page_endpoint(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

def invoke_get_login_page(payload: dict) -> dict:
    """Invoke get login page endpoint"""
    try:
        request = LoginPageGetRequest(**payload)
        result = asyncio.run(content_endpoints.get_login_page(request))
        
        response_data = result.model_dump() if hasattr(result, "model_dump") else result.dict() if hasattr(result, "dict") else result
        
        return {
            "data": response_data,
            "model_time_ms": 0,
            "timing": 0.0
        }
    except Exception as e:
        return {
            "data": {"success": False, "error": str(e), "error_type": type(e).__name__},
            "model_time_ms": 0,
            "timing": 0.0
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        reload=os.getenv("DEBUG") == "True",
        log_level=os.getenv("LOG_LEVEL").lower()
    )