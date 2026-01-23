from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class ErrorPageCreateRequest(BaseModel):
    """Schema for creating market-specific error pages"""
    page_path_404: str = Field(..., description="Full page path for the 404 error page")
    page_path_500: str = Field(..., description="Full page path for the 500 error page")
    jcr_content_404: Dict[str, Any] = Field(
        ...,
        description="JCR content structure for 404 error page to update the existing page."
    )
    jcr_content_500: Dict[str, Any] = Field(
        ...,
        description="JCR content structure for 500 error page to update the existing page."
    )


class ErrorPageCreateResponse(BaseModel):
    """Schema for error page creation response"""
    success: bool
    message: str


class ErrorPageGetRequest(BaseModel):
    """Schema for fetching error pages"""
    page_path_404: str = Field(..., description="Full page path for the 404 error page")
    page_path_500: str = Field(..., description="Full page path for the 500 error page")


class ErrorPageGetResponse(BaseModel):
    """Schema for error page retrieval response"""
    success: bool
    message: str
    page_404: Optional[Dict[str, Any]] = Field(None, description="404 error page content and metadata")
    page_500: Optional[Dict[str, Any]] = Field(None, description="500 error page content and metadata")
    error_details: Optional[str] = None


class ProtectedPageCreateRequest(BaseModel):
    """Schema for updating protected page"""
    page_path: str = Field(..., description="Full page path for the protected page")
    jcr_content: Dict[str, Any] = Field(
        ...,
        description="JCR content structure for protected page to update the existing page."
    )


class ProtectedPageCreateResponse(BaseModel):
    """Schema for protected page update response"""
    success: bool
    message: str
    page_path: Optional[str] = None
    error_details: Optional[str] = None


class ProtectedPageGetRequest(BaseModel):
    """Schema for fetching protected page"""
    page_path: str = Field(..., description="Full page path for the protected page")


class ProtectedPageGetResponse(BaseModel):
    """Schema for protected page retrieval response"""
    success: bool
    message: str
    page_content: Optional[Dict[str, Any]] = Field(None, description="Protected page content and metadata")
    error_details: Optional[str] = None


class HcpModalPopupCreateRequest(BaseModel):
    """Schema for updating HCP modal popup page"""
    page_path: str = Field(..., description="Full page path for the HCP modal popup page")
    jcr_content: Dict[str, Any] = Field(
        ...,
        description="JCR content structure for HCP modal popup to update the existing page."
    )


class HcpModalPopupCreateResponse(BaseModel):
    """Schema for HCP modal popup update response"""
    success: bool
    message: str
    page_path: Optional[str] = None
    error_details: Optional[str] = None


class HcpModalPopupGetRequest(BaseModel):
    """Schema for fetching HCP modal popup page"""
    page_path: str = Field(..., description="Full page path for the HCP modal popup page")


class HcpModalPopupGetResponse(BaseModel):
    """Schema for HCP modal popup retrieval response"""
    success: bool
    message: str
    page_content: Optional[Dict[str, Any]] = Field(None, description="HCP modal popup page content and metadata")
    error_details: Optional[str] = None


class LoginPageCreateRequest(BaseModel):
    """Schema for updating login page"""
    page_path: str = Field(..., description="Full page path for the login page")
    jcr_content: Dict[str, Any] = Field(
        ...,
        description="JCR content structure for login page to update the existing page."
    )


class LoginPageCreateResponse(BaseModel):
    """Schema for login page update response"""
    success: bool
    message: str
    page_path: Optional[str] = None
    error_details: Optional[str] = None


class LoginPageGetRequest(BaseModel):
    """Schema for fetching login page"""
    page_path: str = Field(..., description="Full page path for the login page")


class LoginPageGetResponse(BaseModel):
    """Schema for login page retrieval response"""
    success: bool
    message: str
    page_content: Optional[Dict[str, Any]] = Field(None, description="Login page content and metadata")
    error_details: Optional[str] = None


class ImageUploadResponse(BaseModel):
    """Schema for image and PDF upload response"""
    success: bool
    message: str
    uploaded_images: Optional[List[Dict[str, Any]]] = Field(None, description="Details of uploaded image files")
    uploaded_pdfs: Optional[List[Dict[str, Any]]] = Field(None, description="Details of uploaded PDF files")
    error_details: Optional[str] = None


class DAMFolderCreateRequest(BaseModel):
    """Schema for creating DAM folder structure"""
    dam_path: str = Field(..., description="Base DAM path (e.g., /content/dam/buildeasy/mava)")
    market: str = Field(..., description="Market name (e.g., India)")
    locale: str = Field(..., description="Locale code (e.g., En)")
    site: str = Field(..., description="Site type: 'HCP', 'Patient', or 'Both'")


class DAMFolderCreateResponse(BaseModel):
    """Schema for DAM folder creation response"""
    success: bool
    message: str
    hcp_images_path: Optional[str] = Field(None, description="Path to HCP Images folder")
    hcp_pdfs_path: Optional[str] = Field(None, description="Path to HCP PDFs folder")
    patient_images_path: Optional[str] = Field(None, description="Path to Patient Images folder")
    patient_pdfs_path: Optional[str] = Field(None, description="Path to Patient PDFs folder")
    error_details: Optional[str] = None
