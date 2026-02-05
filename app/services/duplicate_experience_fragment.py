"""
Service module for duplicating experience fragments in AEM.
"""

from typing import Dict, Any
from app.services.aem_utils import AEMClient
from app.core.logging import logger


async def duplicate_experience_fragment(
    xf_path: str,
    market_region: str
) -> Dict[str, Any]:
    """
    Duplicate an experience fragment folder and rename it with the new market region.
    
    Args:
        xf_path: Source experience fragment path to duplicate
        market_region: New market region name for the duplicated experience fragment
        
    Returns:
        dict: Result containing success status, new path, and message
    """
    try:
        logger.info(f"Duplicating experience fragment from {xf_path} with market region: {market_region}")
        
        # Sanitize market region name: convert to lowercase and replace spaces with hyphens
        market_sanitized = market_region.lower().replace(" ", "-")
        
        # Extract the parent path
        path_parts = xf_path.rstrip("/").split("/")
        # Go up two levels to get the parent of the parent
        # This prevents double nesting when AEM copies the folder
        parent_of_parent = "/".join(path_parts[:-1])
        
        # Use market region as the new folder name and title
        new_folder_name = market_sanitized
        new_folder_title = market_region
        new_xf_path = f"{parent_of_parent}/{new_folder_name}"
        
        # Use AEM client to duplicate
        async with AEMClient() as aem:
            # Test connection
            is_connected = await aem.test_connection()
            if not is_connected:
                return {
                    "success": False,
                    "error": "Cannot connect to AEM instance",
                    "new_xf_path": None
                }
            
            # Build copy operation data directly
            copy_url = f"{aem.host}{xf_path}"
            copy_data = {
                ":operation": "copy",
                ":dest": new_xf_path,
                ":replace": "true",
                "_charset_": "utf-8"
            }
            
            # Execute copy operation
            logger.info(f"Copying from {xf_path} to {new_xf_path}")
            response = await aem.client.post(copy_url, data=copy_data, headers=aem._get_headers())
            response.raise_for_status()
            
            logger.info(f"Successfully copied experience fragment to {new_xf_path}")
            
            # Update the title and additional properties
            update_data = {
                "jcr:content/jcr:title": new_folder_title,
                "_charset_": "utf-8"
            }
            
            # Update the new experience fragment
            update_url = f"{aem.host}{new_xf_path}"
            update_response = await aem.client.post(update_url, data=update_data, headers=aem._get_headers())
            update_response.raise_for_status()
            
            logger.info(f"Successfully updated experience fragment properties for {new_xf_path}")
            
            result = {
                "success": True,
                "new_path": new_xf_path
            }
            
            if result.get("success"):
                logger.info(f"Successfully duplicated experience fragment to {new_xf_path}")
                
                return {
                    "success": True,
                    "new_xf_path": new_xf_path,
                    "message": f"Successfully duplicated experience fragment to {new_xf_path}"
                }
            else:
                error = result.get("error", "Unknown error occurred during duplication")
                logger.error(f"Experience fragment duplication failed: {error}")
                
                return {
                    "success": False,
                    "error": error,
                    "new_xf_path": None
                }
                
    except Exception as e:
        error_message = f"Error duplicating experience fragment: {str(e)}"
        logger.error(error_message)
        
        return {
            "success": False,
            "error": error_message,
            "new_xf_path": None
        }
