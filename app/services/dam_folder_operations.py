"""
DAM Folder Operations
Functions responsible for creating and managing DAM folder structures in AEM.
"""

from typing import Dict, Any, Optional
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
