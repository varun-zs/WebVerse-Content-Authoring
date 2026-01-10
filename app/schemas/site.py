from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DuplicateTemplateRequest(BaseModel):
    """Schema for duplicating an empty page template"""
    market_region: str = Field(..., description="Market region (e.g., 'india', 'germany', 'usa', 'uk', 'france')")
    source_path: str = Field(..., description="Source template path to duplicate from")


class DuplicateTemplateResponse(BaseModel):
    """Schema for duplicate template response"""
    success: bool
    new_template_path: Optional[str] = None
    error_details: Optional[str] = None


class ListPagesRequest(BaseModel):
    """Schema for listing pages from an AEM site"""
    site_path: str = Field(..., description="AEM site path (e.g., '/content/commercial/mava-international')")


class ListPagesResponse(BaseModel):
    """Schema for list pages response"""
    success: bool
    jcr_content: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None

