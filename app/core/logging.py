import sys
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()


def setup_logging():
    """Setup logging configuration"""
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format=os.getenv("LOG_FORMAT"),
        level=os.getenv("LOG_LEVEL"),
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Add file logger for production
    if os.getenv("ENVIRONMENT") == "production":
        logger.add(
            "logs/app.log",
            rotation="500 MB",
            retention="10 days",
            format=os.getenv("LOG_FORMAT"),
            level=os.getenv("LOG_LEVEL"),
            backtrace=True,
            diagnose=False  # Don't include sensitive data in production logs
        )
    
    logger.info(f"Logging setup complete - Level: {os.getenv('LOG_LEVEL')}")


# Export logger for use throughout the application
__all__ = ["logger", "setup_logging"]
