"""
DAM Folder Operations
Functions responsible for creating and managing DAM folder structures in AEM.
"""

import os
import base64
from typing import Dict, Any, Optional, List
from app.core.logging import logger
from app.services.aem_utils import AEMClient


async def check_folder_exists(aem_client: AEMClient, folder_path: str) -> bool:
    """Check if a folder exists in AEM DAM
    
    Args:
        aem_client: AEM client instance
        folder_path: Full path to the folder
        
    Returns:
        bool: True if folder exists, False otherwise
    """
    try:
        url = f"{aem_client.host}{folder_path}"
        response = await aem_client.client.get(url)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error checking folder existence at {folder_path}: {e}")
        return False


async def create_dam_folder(aem_client: AEMClient, folder_path: str, folder_title: str) -> bool:
    """Create a single folder in AEM DAM
    
    Args:
        aem_client: AEM client instance
        folder_path: Full path where the folder should be created
        folder_title: Display title for the folder
        
    Returns:
        bool: True if creation successful, False otherwise
    """
    try:
        logger.info(f"Creating DAM folder: {folder_path}")
        
        url = f"{aem_client.host}{folder_path}"
        
        # DAM folder creation data
        folder_data = {
            "jcr:primaryType": "sling:Folder",
            "jcr:title": folder_title,
            "_charset_": "utf-8"
        }
        
        response = await aem_client.client.post(url, data=folder_data)
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully created folder: {folder_path}")
            return True
        else:
            logger.error(f"Failed to create folder {folder_path}. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating folder {folder_path}: {e}")
        return False


async def create_folder_structure(
    aem_client: AEMClient,
    dam_path: str,
    market: str,
    locale: str,
    site: str
) -> Dict[str, Any]:
    """Create complete DAM folder structure for market/locale/site
    
    Args:
        aem_client: AEM client instance
        dam_path: Base DAM path (e.g., /content/dam/buildeasy/mava)
        market: Market name (e.g., India)
        locale: Locale code (e.g., En)
        site: Site type - 'HCP', 'Patient', or 'Both'
        
    Returns:
        dict: Result with folder paths and success status
    """
    try:
        logger.info(f"Creating DAM folder structure for Market: {market}, Locale: {locale}, Site: {site}")
        
        # Validate site parameter
        site = site.upper()
        if site not in ['HCP', 'PATIENT', 'BOTH']:
            return {
                "success": False,
                "error": "Invalid site type. Must be 'HCP', 'Patient', or 'Both'"
            }
        
        # Remove trailing slash from dam_path
        dam_path = dam_path.rstrip('/')
        
        # Build folder paths
        market_path = f"{dam_path}/{market}"
        locale_path = f"{market_path}/{locale}"
        
        result = {
            "success": True,
            "hcp_images_path": None,
            "hcp_pdfs_path": None,
            "patient_images_path": None,
            "patient_pdfs_path": None,
            "created_folders": []
        }
        
        # Step 1: Check/Create Market folder
        if not await check_folder_exists(aem_client, market_path):
            if not await create_dam_folder(aem_client, market_path, market):
                return {
                    "success": False,
                    "error": f"Failed to create market folder: {market_path}"
                }
            result["created_folders"].append(market_path)
        else:
            logger.info(f"Market folder already exists: {market_path}")
        
        # Step 2: Check/Create Locale folder
        if not await check_folder_exists(aem_client, locale_path):
            if not await create_dam_folder(aem_client, locale_path, locale):
                return {
                    "success": False,
                    "error": f"Failed to create locale folder: {locale_path}"
                }
            result["created_folders"].append(locale_path)
        else:
            logger.info(f"Locale folder already exists: {locale_path}")
        
        # Step 3: Create site-specific folders
        sites_to_create = []
        if site == 'HCP':
            sites_to_create = ['HCP']
        elif site == 'PATIENT':
            sites_to_create = ['Patient']
        elif site == 'BOTH':
            sites_to_create = ['HCP', 'Patient']
        
        for site_type in sites_to_create:
            site_path = f"{locale_path}/{site_type}"
            
            # Create site folder (HCP or Patient)
            if not await check_folder_exists(aem_client, site_path):
                if not await create_dam_folder(aem_client, site_path, site_type):
                    return {
                        "success": False,
                        "error": f"Failed to create site folder: {site_path}"
                    }
                result["created_folders"].append(site_path)
            else:
                logger.info(f"Site folder already exists: {site_path}")
            
            # Create Images folder
            images_path = f"{site_path}/Images"
            if not await check_folder_exists(aem_client, images_path):
                if not await create_dam_folder(aem_client, images_path, "Images"):
                    return {
                        "success": False,
                        "error": f"Failed to create Images folder: {images_path}"
                    }
                result["created_folders"].append(images_path)
            else:
                logger.info(f"Images folder already exists: {images_path}")
            
            # Create PDFs folder
            pdfs_path = f"{site_path}/PDFs"
            if not await check_folder_exists(aem_client, pdfs_path):
                if not await create_dam_folder(aem_client, pdfs_path, "PDFs"):
                    return {
                        "success": False,
                        "error": f"Failed to create PDFs folder: {pdfs_path}"
                    }
                result["created_folders"].append(pdfs_path)
            else:
                logger.info(f"PDFs folder already exists: {pdfs_path}")
            
            # Store paths in result
            if site_type == 'HCP':
                result["hcp_images_path"] = images_path
                result["hcp_pdfs_path"] = pdfs_path
            elif site_type == 'Patient':
                result["patient_images_path"] = images_path
                result["patient_pdfs_path"] = pdfs_path
        
        folders_created = len(result["created_folders"])
        if folders_created > 0:
            result["message"] = f"Successfully created {folders_created} folder(s)"
        else:
            result["message"] = "All folders already exist"
        
        logger.info(f"Folder structure creation completed: {result['message']}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating folder structure: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def upload_file_to_dam_base64(
    aem_client: AEMClient,
    filename: str,
    content_base64: str,
    content_type: str,
    dam_path: str,
    file_type: str = "image"
) -> Dict[str, Any]:
    """Upload a single file from Base64 encoded content to AEM DAM
    
    Args:
        aem_client: AEM client instance
        filename: Name of the file
        content_base64: Base64 encoded file content
        content_type: MIME type of the file
        dam_path: DAM path where the file should be uploaded
        file_type: Type of file - "image" or "pdf"
        
    Returns:
        dict: Result with success status and file details
    """
    try:
        logger.info(f"Uploading {file_type} '{filename}' to DAM path: {dam_path}")
        
        # Decode Base64 content
        try:
            file_content = base64.b64decode(content_base64)
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid Base64 encoding: {str(e)}",
                "filename": filename
            }
        
        # Validate file type based on file_type parameter
        if file_type.lower() == "image":
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico'}
        elif file_type.lower() == "pdf":
            allowed_extensions = {'.pdf'}
        else:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico', '.pdf'}
        
        file_extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_extension not in allowed_extensions:
            return {
                "success": False,
                "error": f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
                "filename": filename
            }
        
        # Get DAM root from environment variable
        dam_root = os.getenv("AEM_ASSETS_ROOT", "/content/dam")
        
        # Ensure dam_path starts with the DAM root
        if not dam_path.startswith(dam_root):
            dam_path = f"{dam_root}/{dam_path.lstrip('/')}"
        
        # Construct the upload URL
        upload_url = f"{aem_client.host}{dam_path}.createasset.html"
        
        # Prepare multipart form data for AEM DAM upload
        files_data = {
            'file': (filename, file_content, content_type)
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
            asset_path = f"{dam_path}/{filename}"
            logger.info(f"Successfully uploaded {file_type}: {filename} to {asset_path}")
            return {
                "success": True,
                "filename": filename,
                "dam_path": asset_path,
                "size_bytes": len(file_content),
                "content_type": content_type,
                "message": f"{file_type.capitalize()} uploaded successfully to {asset_path}"
            }
        else:
            error_msg = f"Failed to upload {file_type}. Status: {response.status_code}, Response: {response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "filename": filename
            }
            
    except Exception as e:
        logger.error(f"Error uploading {file_type} '{filename}': {e}")
        return {
            "success": False,
            "error": str(e),
            "filename": filename
        }


async def upload_files_to_dam_base64(
    aem_client: AEMClient,
    images: Optional[List[Dict[str, str]]] = None,
    images_path: Optional[str] = None,
    pdfs: Optional[List[Dict[str, str]]] = None,
    pdfs_path: Optional[str] = None
) -> Dict[str, Any]:
    """Upload images and PDFs from Base64 encoded content to AEM DAM
    
    Args:
        aem_client: AEM client instance
        images: List of image file dicts with 'filename', 'content', 'content_type'
        images_path: DAM path where images should be uploaded
        pdfs: List of PDF file dicts with 'filename', 'content', 'content_type'
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
                result = await upload_file_to_dam_base64(
                    aem_client=aem_client,
                    filename=image.get("filename"),
                    content_base64=image.get("content"),
                    content_type=image.get("content_type"),
                    dam_path=images_path,
                    file_type="image"
                )
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
                result = await upload_file_to_dam_base64(
                    aem_client=aem_client,
                    filename=pdf.get("filename"),
                    content_base64=pdf.get("content"),
                    content_type=pdf.get("content_type"),
                    dam_path=pdfs_path,
                    file_type="pdf"
                )
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
