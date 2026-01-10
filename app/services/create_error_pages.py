"""
Error Page Creation Functions
Functions responsible for creating error pages (404/500) in AEM.
"""

from typing import Dict, Any
from app.core.logging import logger
from app.services.aem_utils import AEMClient


async def create_error_page(aem_client: AEMClient, page_path: str, error_type: str, custom_jcr_content: Dict[str, Any]) -> dict:
    """Update existing error page (404 or 500) with JCR content"""
    try:
        logger.info(f"Updating {error_type} error page at: {page_path}")
        
        if not custom_jcr_content:
            error_msg = f"No JCR content provided for {error_type} error page. JCR content is required to update the page."
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "page_path": page_path,
                "error_type": error_type
            }
        
        logger.info(f"Updating {error_type} error page with custom JCR content")
        
        # Prepare the JCR content for update
        page_data = custom_jcr_content.copy()
        # Ensure charset is set
        page_data["_charset_"] = "utf-8"
        
        # Update the page directly with custom JCR content
        page_update_success = await update_page_with_jcr_content(aem_client, page_path, page_data)
        
        if not page_update_success:
            raise Exception(f"Failed to update error page with JCR content at {page_path}")
        
        logger.info(f"Successfully updated {error_type} error page with JCR content")
        
        return {
            "success": True,
            "page_path": page_path,
            "error_type": error_type,
            "update_method": "custom_jcr_content",
            "message": f"Page updated at {page_path}"
        }
            
    except Exception as e:
        logger.error(f"Error updating {error_type} error page: {e}")
        return {
            "success": False,
            "error": str(e),
            "page_path": page_path,
            "error_type": error_type
        }


async def update_page_with_jcr_content(aem_client: AEMClient, page_path: str, jcr_content: dict) -> bool:
    """Update an existing page with custom JCR content"""
    try:
        logger.info(f"Updating page with custom JCR content at: {page_path}")
        
        # Post the JCR content to update the page
        response = await aem_client.client.post(f"{aem_client.host}{page_path}", data=jcr_content)
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully updated page with JCR content: {page_path}")
            return True
        else:
            logger.error(f"Failed to update page. Status code: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating page with JCR content: {e}")
        return False