from fastapi import APIRouter, HTTPException, status
from app.schemas.site import (
    DuplicateTemplateRequest, DuplicateTemplateResponse,
    ListPagesRequest, ListPagesResponse
)
from app.services.aem_utils import AEMClient
from app.core.logging import logger

router = APIRouter()


@router.post("/duplicate-template", response_model=DuplicateTemplateResponse)
async def duplicate_empty_template(request: DuplicateTemplateRequest):
    """
    Duplicate the empty page template (mava-template) for a specific market region.
    
    This endpoint copies the empty page template from the specified source_path
    and creates a new page with the market region information.
    
    The new template will be created at: /content/commercial/mava-international/hcp-{market_region}
    
    Args:
        request: DuplicateTemplateRequest containing market_region and source_path
        
    Returns:
        DuplicateTemplateResponse with success status and new template path
    """
    try:
        # Source template path (from request)
        source_template_path = request.source_path
        destination_parent_path = "/content/buildeasy/mava"
        
        # Create new page name from market region
        # Sanitize input: convert to lowercase and replace spaces with hyphens
        market_sanitized = request.market_region.lower().replace(" ", "-")
        new_page_name = f"hcp-{market_sanitized}"
        new_page_title = f"hcp-{request.market_region}"
        
        logger.info(f"Duplicating template for market: {request.market_region}")
        
        # Use default AEM credentials from configuration
        async with AEMClient() as aem:
            # Test connection first
            is_connected = await aem.test_connection()
            if not is_connected:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot connect to AEM instance"
                )
            
            # Duplicate the template with additional properties
            additional_properties = {
                "marketRegion": request.market_region,
                "templateType": "duplicated-mava-template",
                "sourceTemplate": source_template_path
            }
            
            result = await aem.duplicate_page_template(
                source_path=source_template_path,
                destination_parent_path=destination_parent_path,
                new_page_name=new_page_name,
                new_page_title=new_page_title,
                additional_properties=additional_properties
            )
            
            if result.get("success"):
                new_path = result.get("new_path")
                logger.info(f"Template duplication successful: {new_path}")
                
                return DuplicateTemplateResponse(
                    success=True,
                    new_template_path=new_path
                )
            else:
                error = result.get("error", "Unknown error occurred")
                logger.error(f"Template duplication failed: {error}")
                
                return DuplicateTemplateResponse(
                    success=False,
                    new_template_path=None,
                    error_details=error
                )
    
    except HTTPException:
        raise
    except Exception as e:
        error_message = f"Error duplicating template for {request.market_region}: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post("/list-pages", response_model=ListPagesResponse)
async def list_pages(request: ListPagesRequest):
    """
    List all pages and JCR nodes under a specific AEM site path.
    
    This endpoint retrieves all JCR content including child pages and nodes from the specified
    site path on the AEM platform.
    
    The endpoint uses AEM's .infinity.json selector to fetch the complete JCR tree structure
    including all properties, child nodes, and nested pages.
    
    Args:
        request: ListPagesRequest containing the site_path
        
    Returns:
        ListPagesResponse with success status and complete JCR content tree
        
    Example:
        Request:
        ```json
        {
            "site_path": "/content/commercial/mava-international"
        }
        ```
        
        Response:
        ```json
        {
            "success": true,
            "site_path": "/content/commercial/mava-international",
            "jcr_content": {
                "jcr:primaryType": "cq:Page",
                "jcr:content": { ... },
                "child-page-1": { ... },
                "child-page-2": { ... }
            }
        }
        ```
    """
    try:
        logger.info(f"Listing pages from site path: {request.site_path}")
        
        # Use default AEM credentials from configuration
        async with AEMClient() as aem:
            # Test connection first
            is_connected = await aem.test_connection()
            if not is_connected:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot connect to AEM instance"
                )
            
            # Get all pages and JCR content from the site path
            try:
                jcr_content = await aem.list_pages(request.site_path)
                
                if jcr_content:
                    logger.info(f"Successfully retrieved JCR content from: {request.site_path}")
                    
                    return ListPagesResponse(
                        success=True,
                        jcr_content=jcr_content
                    )
                else:
                    logger.warning(f"No content found at site path: {request.site_path}")
                    
                    return ListPagesResponse(
                        success=False,
                        error_details=f"No content found at path: {request.site_path}"
                    )
                    
            except Exception as e:
                logger.error(f"Error retrieving pages from {request.site_path}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Site path not found or inaccessible: {request.site_path}"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        error_message = f"Error listing pages from {request.site_path}: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )
