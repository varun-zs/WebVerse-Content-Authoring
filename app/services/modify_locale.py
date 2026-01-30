"""
Locale Modification Functions
Functions responsible for modifying site locale in AEM.
"""

from typing import Dict, Any, Optional
from app.core.logging import logger
from app.services.aem_utils import AEMClient


async def modify_site_locale(aem_client: AEMClient, page_path: str, custom_jcr_content: Optional[Dict[str, Any]] = None) -> dict:
    """Modify site locale with optional JCR content"""
    try:
        logger.info(f"Modifying locale for site at: {page_path}")
        
        if custom_jcr_content is None:
            logger.info("No JCR content provided. Skipping locale modification.")
            return {
                "success": True,
                "skipped": True,
                "page_path": page_path,
                "message": "Locale modification skipped - no content provided"
            }
        
        if not custom_jcr_content:
            error_msg = "Empty JCR content provided for locale modification. JCR content cannot be empty."
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "page_path": page_path
            }
        
        logger.info("Modifying site locale with custom JCR content")
        
        # Prepare the JCR content for update
        page_data = custom_jcr_content.copy()
        # Ensure charset is set
        page_data["_charset_"] = "utf-8"
        
        # Update the page directly with custom JCR content
        page_update_success = await update_page_with_jcr_content(aem_client, page_path, page_data)
        
        if not page_update_success:
            raise Exception(f"Failed to modify locale with JCR content at {page_path}")
        
        logger.info("Successfully modified site locale with JCR content")
        
        return {
            "success": True,
            "page_path": page_path,
            "update_method": "custom_jcr_content",
            "message": f"Locale modified at {page_path}"
        }
            
    except Exception as e:
        logger.error(f"Error modifying site locale: {e}")
        return {
            "success": False,
            "error": str(e),
            "page_path": page_path
        }


async def update_page_with_jcr_content(aem_client: AEMClient, page_path: str, jcr_content: dict) -> bool:
    """Update an existing page with custom JCR content"""
    try:
        logger.info(f"Updating page with JCR content at: {page_path}")
        
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
