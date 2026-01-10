from fastapi import APIRouter, HTTPException, status
from app.schemas.content import (
    ErrorPageCreateRequest, ErrorPageCreateResponse,
    ErrorPageGetRequest, ErrorPageGetResponse,
    ProtectedPageCreateRequest, ProtectedPageCreateResponse,
    ProtectedPageGetRequest, ProtectedPageGetResponse,
    HcpModalPopupCreateRequest, HcpModalPopupCreateResponse,
    HcpModalPopupGetRequest, HcpModalPopupGetResponse,
    LoginPageCreateRequest, LoginPageCreateResponse,
    LoginPageGetRequest, LoginPageGetResponse
)
from app.services.aem_utils import AEMClient
from app.services.create_error_pages import create_error_page
from app.services.create_protected_pages import update_protected_page
from app.services.create_popup_pages import update_hcp_modal_popup
from app.services.create_login_pages import update_login_page
from app.core.logging import logger

router = APIRouter()

# ---- Adobe AEM Error Pages Content Authoring Functions ----


@router.post("/create-error-pages", response_model=ErrorPageCreateResponse)
async def create_error_pages(request: ErrorPageCreateRequest):
    """Create both 404 and 500 error page components with market-specific content"""
    try:
        async with AEMClient() as aem:
            # Update 404 error page
            result_404 = await create_error_page(
                aem_client=aem,
                page_path=request.page_path_404,
                error_type="404",
                custom_jcr_content=request.jcr_content_404
            )
            
            # Update 500 error page
            result_500 = await create_error_page(
                aem_client=aem,
                page_path=request.page_path_500,
                error_type="500",
                custom_jcr_content=request.jcr_content_500
            )
            
            # Check if both were successful
            all_successful = result_404.get("success", False) and result_500.get("success", False)
            
            if all_successful:
                message = "Successfully updated 404 and 500 error pages"
                logger.info(message)
            else:
                message = "Partial success: Some error page updates failed"
                logger.warning(message)
            
            return ErrorPageCreateResponse(
                success=all_successful,
                message=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating error pages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create error pages: {str(e)}"
        )


@router.post("/error-pages", response_model=ErrorPageGetResponse)
async def get_error_pages(request: ErrorPageGetRequest):
    """Fetch details of both 404 and 500 error pages"""
    try:
        async with AEMClient() as aem:
            page_404_content = None
            page_500_content = None
            errors = []
            
            # Fetch 404 page content
            try:
                page_404_content = await aem.get_page_content(request.page_path_404)
                logger.info(f"Successfully fetched 404 error page: {request.page_path_404}")
            except Exception as e:
                error_msg = f"Failed to fetch 404 page at {request.page_path_404}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Fetch 500 page content
            try:
                page_500_content = await aem.get_page_content(request.page_path_500)
                logger.info(f"Successfully fetched 500 error page: {request.page_path_500}")
            except Exception as e:
                error_msg = f"Failed to fetch 500 page at {request.page_path_500}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Determine overall success
            success = page_404_content is not None and page_500_content is not None
            
            if success:
                message = "Successfully retrieved both error pages"
            elif page_404_content or page_500_content:
                message = "Partially retrieved error pages"
            else:
                message = "Failed to retrieve error pages"
            
            return ErrorPageGetResponse(
                success=success,
                message=message,
                page_404=page_404_content,
                page_500=page_500_content,
                error_details="; ".join(errors) if errors else None
            )
            
    except Exception as e:
        logger.error(f"Error fetching error pages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch error pages: {str(e)}"
        )


# ---- End of Adobe AEM Error Pages Content Authoring Functions ----

# ---- Adobe AEM Protected Pages Content Authoring Functions ----


@router.post("/protected-page", response_model=ProtectedPageCreateResponse)
async def create_protected_page(request: ProtectedPageCreateRequest):
    """
    Update protected page with JCR content.
    
    This endpoint updates an existing protected page with the provided JCR content.
    
    Args:
        request: ProtectedPageCreateRequest with page_path and jcr_content
        
    Returns:
        ProtectedPageCreateResponse with detailed result of the page update
    """
    try:
        async with AEMClient() as aem:
            page_result = await update_protected_page(
                aem_client=aem,
                page_path=request.page_path,
                custom_jcr_content=request.jcr_content
            )
        
        # Determine success and create appropriate message
        page_success = page_result.get("success", False)
        
        if page_success:
            message = "Successfully updated protected page"
            page_path = page_result.get("page_path")
        else:
            message = "Failed to update protected page"
            page_path = None
        
        logger.info(f"Protected page update result: {message}")
        
        return ProtectedPageCreateResponse(
            success=page_success,
            message=message,
            page_path=page_path,
            error_details=page_result.get("error") if not page_success else None
        )
        
    except Exception as e:
        error_message = f"Failed to update protected page: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post("/get-protected-page", response_model=ProtectedPageGetResponse)
async def get_protected_page(request: ProtectedPageGetRequest):
    """Fetch details of protected page"""
    try:
        async with AEMClient() as aem:
            page_content = None
            error_msg = None
            
            # Fetch protected page content
            try:
                page_content = await aem.get_page_content(request.page_path)
                logger.info(f"Successfully fetched protected page: {request.page_path}")
            except Exception as e:
                error_msg = f"Failed to fetch protected page at {request.page_path}: {str(e)}"
                logger.error(error_msg)
            
            # Determine success
            success = page_content is not None
            
            if success:
                message = "Successfully retrieved protected page"
            else:
                message = "Failed to retrieve protected page"
            
            return ProtectedPageGetResponse(
                success=success,
                message=message,
                page_content=page_content,
                error_details=error_msg
            )
            
    except Exception as e:
        logger.error(f"Error fetching protected page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch protected page: {str(e)}"
        )


# ---- End of Adobe AEM Protected Pages Content Authoring Functions ----

# ---- Adobe AEM HCP Modal Popup Content Authoring Functions ----


@router.post("/create-hcp-modal-popup", response_model=HcpModalPopupCreateResponse)
async def create_hcp_modal_popup_endpoint(request: HcpModalPopupCreateRequest):
    """
    Update HCP modal popup page with JCR content.
    
    This endpoint updates an existing HCP modal popup page with the provided JCR content.
    
    Args:
        request: HcpModalPopupCreateRequest with page_path and jcr_content
        
    Returns:
        HcpModalPopupCreateResponse with detailed result of the popup update
    """
    try:
        async with AEMClient() as aem:
            popup_result = await update_hcp_modal_popup(
                aem_client=aem,
                page_path=request.page_path,
                custom_jcr_content=request.jcr_content
            )
        
        # Determine success and create appropriate message
        popup_success = popup_result.get("success", False)
        
        if popup_success:
            message = "Successfully updated HCP modal popup"
            page_path = popup_result.get("page_path")
        else:
            message = "Failed to update HCP modal popup"
            page_path = None
        
        logger.info(f"HCP modal popup update result: {message}")
        
        return HcpModalPopupCreateResponse(
            success=popup_success,
            message=message,
            page_path=page_path,
            error_details=popup_result.get("error") if not popup_success else None
        )
        
    except Exception as e:
        error_message = f"Failed to update HCP modal popup: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post("/hcp-modal-popup", response_model=HcpModalPopupGetResponse)
async def get_hcp_modal_popup(request: HcpModalPopupGetRequest):
    """Fetch details of HCP modal popup page"""
    try:
        async with AEMClient() as aem:
            page_content = None
            error_msg = None
            
            # Fetch HCP modal popup page content
            try:
                page_content = await aem.get_page_content(request.page_path)
                logger.info(f"Successfully fetched HCP modal popup page: {request.page_path}")
            except Exception as e:
                error_msg = f"Failed to fetch HCP modal popup page at {request.page_path}: {str(e)}"
                logger.error(error_msg)
            
            # Determine success
            success = page_content is not None
            
            if success:
                message = "Successfully retrieved HCP modal popup page"
            else:
                message = "Failed to retrieve HCP modal popup page"
            
            return HcpModalPopupGetResponse(
                success=success,
                message=message,
                page_content=page_content,
                error_details=error_msg
            )
            
    except Exception as e:
        logger.error(f"Error fetching HCP modal popup page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch HCP modal popup page: {str(e)}"
        )


# ---- End of Adobe AEM HCP Modal Popup Content Authoring Functions ----

# ---- Adobe AEM Login Page Content Authoring Functions ----


@router.post("/create-login-page", response_model=LoginPageCreateResponse)
async def create_login_page_endpoint(request: LoginPageCreateRequest):
    """
    Update login page with JCR content.
    
    This endpoint updates an existing login page with the provided JCR content.
    
    Args:
        request: LoginPageCreateRequest with page_path and jcr_content
        
    Returns:
        LoginPageCreateResponse with detailed result of the page update
    """
    try:
        async with AEMClient() as aem:
            login_result = await update_login_page(
                aem_client=aem,
                page_path=request.page_path,
                custom_jcr_content=request.jcr_content
            )
        
        # Determine success and create appropriate message
        login_success = login_result.get("success", False)
        
        if login_success:
            message = "Successfully updated login page"
            page_path = login_result.get("page_path")
        else:
            message = "Failed to update login page"
            page_path = None
        
        logger.info(f"Login page update result: {message}")
        
        return LoginPageCreateResponse(
            success=login_success,
            message=message,
            page_path=page_path,
            error_details=login_result.get("error") if not login_success else None
        )
        
    except Exception as e:
        error_message = f"Failed to update login page: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@router.post("/login-page", response_model=LoginPageGetResponse)
async def get_login_page(request: LoginPageGetRequest):
    """Fetch details of login page"""
    try:
        async with AEMClient() as aem:
            page_content = None
            error_msg = None
            
            # Fetch login page content
            try:
                page_content = await aem.get_page_content(request.page_path)
                logger.info(f"Successfully fetched login page: {request.page_path}")
            except Exception as e:
                error_msg = f"Failed to fetch login page at {request.page_path}: {str(e)}"
                logger.error(error_msg)
            
            # Determine success
            success = page_content is not None
            
            if success:
                message = "Successfully retrieved login page"
            else:
                message = "Failed to retrieve login page"
            
            return LoginPageGetResponse(
                success=success,
                message=message,
                page_content=page_content,
                error_details=error_msg
            )
            
    except Exception as e:
        logger.error(f"Error fetching login page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch login page: {str(e)}"
        )


# ---- End of Adobe AEM Login Page Content Authoring Functions ----
