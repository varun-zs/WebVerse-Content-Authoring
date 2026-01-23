"""
Image and PDF Upload Functions
Functions responsible for uploading images and PDFs to AEM DAM.
"""

import os
from typing import Dict, Any, List, Optional
from fastapi import UploadFile
from app.core.logging import logger
from app.services.aem_utils import AEMClient


async def upload_file_to_dam(
    aem_client: AEMClient, 
    file: UploadFile, 
    dam_path: str,
    file_type: str = "image"
) -> Dict[str, Any]:
    """Upload a single file (image or PDF) to AEM DAM
    
    Args:
        aem_client: AEM client instance
        file: The uploaded file
        dam_path: DAM path where the file should be uploaded (e.g., /content/dam/project/images)
        file_type: Type of file - "image" or "pdf"
        
    Returns:
        dict: Result with success status and file details
    """
    try:
        logger.info(f"Uploading {file_type} '{file.filename}' to DAM path: {dam_path}")
        
        if not file:
            return {
                "success": False,
                "error": "No file provided",
                "filename": None
            }
        
        # Validate file type based on file_type parameter
        if file_type.lower() == "image":
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico'}
        elif file_type.lower() == "pdf":
            allowed_extensions = {'.pdf'}
        else:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico', '.pdf'}
        
        file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            return {
                "success": False,
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
                "filename": file.filename
            }
        
        # Get DAM root from environment variable
        dam_root = os.getenv("AEM_ASSETS_ROOT", "/content/dam")
        
        # Ensure dam_path starts with the DAM root
        if not dam_path.startswith(dam_root):
            # Remove any leading slashes and prepend dam_root
            dam_path = f"{dam_root}/{dam_path.lstrip('/')}"
        
        # Construct the upload URL
        upload_url = f"{aem_client.host}{dam_path}.createasset.html"
        
        # Read file content
        file_content = await file.read()
        
        # Prepare multipart form data for AEM DAM upload
        files_data = {
            'file': (file.filename, file_content, file.content_type)
        }
        
        # Additional form fields required by AEM
        form_data = {
            '_charset_': 'utf-8',
        }
        
        logger.info(f"Posting file to: {upload_url}")
        
        # Upload the file to AEM DAM
        response = await aem_client.client.post(
            upload_url,
            files=files_data,
            data=form_data
        )
        
        if response.status_code in [200, 201]:
            asset_path = f"{dam_path}/{file.filename}"
            logger.info(f"Successfully uploaded {file_type}: {file.filename} to {asset_path}")
            return {
                "success": True,
                "filename": file.filename,
                "dam_path": asset_path,
                "size_bytes": len(file_content),
                "content_type": file.content_type,
                "message": f"{file_type.capitalize()} uploaded successfully to {asset_path}"
            }
        else:
            error_msg = f"Failed to upload {file_type}. Status: {response.status_code}, Response: {response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "filename": file.filename
            }
            
    except Exception as e:
        logger.error(f"Error uploading {file_type} '{file.filename}': {e}")
        return {
            "success": False,
            "error": str(e),
            "filename": file.filename
        }


async def upload_files_to_dam(
    aem_client: AEMClient,
    images: Optional[List[UploadFile]] = None,
    images_path: Optional[str] = None,
    pdfs: Optional[List[UploadFile]] = None,
    pdfs_path: Optional[str] = None
) -> Dict[str, Any]:
    """Upload images and PDFs to AEM DAM
    
    Args:
        aem_client: AEM client instance
        images: List of image files to upload
        images_path: DAM path where images should be uploaded
        pdfs: List of PDF files to upload
        pdfs_path: DAM path where PDFs should be uploaded
        
    Returns:
        dict: Result with success status and all file upload details
    """
    try:
        uploaded_images = []
        uploaded_pdfs = []
        total_successful = 0
        total_failed = 0
        messages = []
        
        # Upload images if provided
        if images and images_path:
            logger.info(f"Uploading {len(images)} image(s) to: {images_path}")
            images_successful = 0
            images_failed = 0
            
            for image in images:
                result = await upload_file_to_dam(aem_client, image, images_path, "image")
                uploaded_images.append(result)
                
                if result.get("success"):
                    images_successful += 1
                else:
                    images_failed += 1
            
            total_successful += images_successful
            total_failed += images_failed
            
            if images_successful > 0:
                messages.append(f"Uploaded {images_successful} of {len(images)} image(s)")
            if images_failed > 0:
                messages.append(f"{images_failed} image(s) failed")
        
        # Upload PDFs if provided
        if pdfs and pdfs_path:
            logger.info(f"Uploading {len(pdfs)} PDF(s) to: {pdfs_path}")
            pdfs_successful = 0
            pdfs_failed = 0
            
            for pdf in pdfs:
                result = await upload_file_to_dam(aem_client, pdf, pdfs_path, "pdf")
                uploaded_pdfs.append(result)
                
                if result.get("success"):
                    pdfs_successful += 1
                else:
                    pdfs_failed += 1
            
            total_successful += pdfs_successful
            total_failed += pdfs_failed
            
            if pdfs_successful > 0:
                messages.append(f"Uploaded {pdfs_successful} of {len(pdfs)} PDF(s)")
            if pdfs_failed > 0:
                messages.append(f"{pdfs_failed} PDF(s) failed")
        
        # Check if nothing was provided
        if not (images or pdfs):
            return {
                "success": False,
                "message": "No files provided for upload",
                "error": "At least one image or PDF must be provided"
            }
        
        # Build final message
        overall_success = total_failed == 0
        message = ". ".join(messages) if messages else "No files uploaded"
        
        return {
            "success": overall_success,
            "message": message,
            "uploaded_images": uploaded_images if uploaded_images else None,
            "uploaded_pdfs": uploaded_pdfs if uploaded_pdfs else None,
            "total_successful": total_successful,
            "total_failed": total_failed
        }
        
    except Exception as e:
        logger.error(f"Error in file upload: {e}")
        return {
            "success": False,
            "message": f"File upload failed: {str(e)}",
            "error": str(e)
        }
