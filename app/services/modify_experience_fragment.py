"""
Experience Fragment Modification Functions
Functions responsible for modifying experience fragments (headers/footers) in AEM.
"""

from typing import Dict, Any, Optional
from app.core.logging import logger
from app.services.aem_utils import AEMClient


async def modify_experience_fragments(
    aem_client: AEMClient,
    protected_header_path: Optional[str] = None,
    protected_header_jcr_content: Optional[Dict[str, Any]] = None,
    protected_footer_path: Optional[str] = None,
    protected_footer_jcr_content: Optional[Dict[str, Any]] = None,
    login_header_path: Optional[str] = None,
    login_header_jcr_content: Optional[Dict[str, Any]] = None,
    login_footer_path: Optional[str] = None,
    login_footer_jcr_content: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Modify experience fragment headers and footers with JCR content.
    
    Args:
        aem_client: AEM client instance
        protected_header_path: Path to protected header XF
        protected_header_jcr_content: JCR content for protected header
        protected_footer_path: Path to protected footer XF
        protected_footer_jcr_content: JCR content for protected footer
        login_header_path: Path to login header XF
        login_header_jcr_content: JCR content for login header
        login_footer_path: Path to login footer XF
        login_footer_jcr_content: JCR content for login footer
    
    Returns:
        dict: Result with success status and update details for each fragment
    """
    try:
        logger.info("Starting experience fragment modification")
        
        results = {
            "protected_header_updated": False,
            "protected_footer_updated": False,
            "login_header_updated": False,
            "login_footer_updated": False
        }
        
        errors = []
        
        # Update protected header
        if protected_header_path and protected_header_jcr_content:
            logger.info(f"Updating protected header at: {protected_header_path}")
            success = await update_experience_fragment(
                aem_client, 
                protected_header_path, 
                protected_header_jcr_content
            )
            results["protected_header_updated"] = success
            if not success:
                errors.append("Failed to update protected header")
        
        # Update protected footer
        if protected_footer_path and protected_footer_jcr_content:
            logger.info(f"Updating protected footer at: {protected_footer_path}")
            success = await update_experience_fragment(
                aem_client, 
                protected_footer_path, 
                protected_footer_jcr_content
            )
            results["protected_footer_updated"] = success
            if not success:
                errors.append("Failed to update protected footer")
        
        # Update login header
        if login_header_path and login_header_jcr_content:
            logger.info(f"Updating login header at: {login_header_path}")
            success = await update_experience_fragment(
                aem_client, 
                login_header_path, 
                login_header_jcr_content
            )
            results["login_header_updated"] = success
            if not success:
                errors.append("Failed to update login header")
        
        # Update login footer
        if login_footer_path and login_footer_jcr_content:
            logger.info(f"Updating login footer at: {login_footer_path}")
            success = await update_experience_fragment(
                aem_client, 
                login_footer_path, 
                login_footer_jcr_content
            )
            results["login_footer_updated"] = success
            if not success:
                errors.append("Failed to update login footer")
        
        # Determine overall success
        any_attempted = any([
            protected_header_path and protected_header_jcr_content,
            protected_footer_path and protected_footer_jcr_content,
            login_header_path and login_header_jcr_content,
            login_footer_path and login_footer_jcr_content
        ])
        
        if not any_attempted:
            logger.info("No experience fragments provided for modification")
            return {
                "success": True,
                "skipped": True,
                "message": "No experience fragments to modify",
                **results
            }
        
        if errors:
            logger.error(f"Experience fragment modification completed with errors: {', '.join(errors)}")
            return {
                "success": False,
                "error": "; ".join(errors),
                "message": "Some experience fragments failed to update",
                **results
            }
        
        logger.info("Successfully modified all provided experience fragments")
        return {
            "success": True,
            "message": "Successfully modified experience fragments",
            **results
        }
            
    except Exception as e:
        logger.error(f"Error modifying experience fragments: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to modify experience fragments",
            **results
        }


async def update_experience_fragment(
    aem_client: AEMClient, 
    xf_path: str, 
    jcr_content: Dict[str, Any]
) -> bool:
    """
    Update an experience fragment with custom JCR content.
    
    Args:
        aem_client: AEM client instance
        xf_path: Path to the experience fragment
        jcr_content: JCR content to update
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        logger.info(f"Updating experience fragment at: {xf_path}")
        
        # Prepare the JCR content for update
        update_data = jcr_content.copy()
        update_data["_charset_"] = "utf-8"
        
        # Post the JCR content to update the experience fragment
        response = await aem_client.client.post(
            f"{aem_client.host}{xf_path}", 
            data=update_data,
            headers=aem_client._get_headers()
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully updated experience fragment: {xf_path}")
            return True
        else:
            logger.error(f"Failed to update experience fragment. Status code: {response.status_code}, Response: {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error updating experience fragment at {xf_path}: {e}")
        return False
