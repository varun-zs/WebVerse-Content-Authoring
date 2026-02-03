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
        
        # Extract the parent path and original folder name
        path_parts = xf_path.rstrip("/").split("/")
        original_folder_name = path_parts[-1]
        destination_parent_path = "/".join(path_parts[:-1])
        
        # Create new folder name with market region
        new_folder_name = f"{original_folder_name}-{market_sanitized}"
        new_folder_title = f"{original_folder_name} - {market_region}"
        
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
            
            # Additional properties for the experience fragment
            additional_properties = {
                "marketRegion": market_region,
                "sourceXF": xf_path
            }
            
            # Duplicate the experience fragment
            result = await aem.duplicate_page_template(
                source_path=xf_path,
                destination_parent_path=destination_parent_path,
                new_page_name=new_folder_name,
                new_page_title=new_folder_title,
                additional_properties=additional_properties
            )
            
            if result.get("success"):
                new_path = result.get("new_path")
                logger.info(f"Successfully duplicated experience fragment to {new_path}")
                
                return {
                    "success": True,
                    "new_xf_path": new_path,
                    "message": f"Successfully duplicated experience fragment to {new_path}"
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
