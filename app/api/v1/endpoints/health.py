from fastapi import APIRouter
import os
from dotenv import load_dotenv
from app.services.aem_utils import AEMClient
from app.core.logging import logger

# Load environment variables from .env file
load_dotenv()

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT")
    }


@router.get("/aem")
async def aem_health():
    """AEM-specific health check with authentication validation"""
    try:
        async with AEMClient() as aem:
            is_connected = await aem.test_connection()
            
            response = {
                "status": "healthy" if is_connected else "unhealthy",
                "aem": "connected" if is_connected else "disconnected",
                "host": os.getenv("AEM_HOST"),
                "authentication": {
                    "method": "basic_auth",
                    "username": os.getenv("AEM_USERNAME")
                }
            }
            
            return response
            
    except Exception as e:
        logger.error(f"AEM health check failed: {e}")
        return {
            "status": "unhealthy",
            "aem": "error",
            "host": os.getenv("AEM_HOST"),
            "error": str(e)
        }
