"""
AEM Utility Functions
Helper functions for AEM operations including market configurations, 
template processing, data format conversion, and AEM client operations.
"""

import httpx
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from app.core.logging import logger

# Load environment variables from .env file
load_dotenv()

# ---- AEM Content Authoring Utils Functions ----

class AEMClient:
    """Adobe AEM HTTP client for content operations with JCR service user support"""
    
    def __init__(self, host: str = None, username: str = None, password: str = None):
        """Initialize AEM client with basic authentication
        
        Args:
            host: AEM host URL
            username: Username for basic auth
            password: Password for basic auth
        """
        self.host = host or os.getenv("AEM_HOST")
        self.username = username or os.getenv("AEM_USERNAME")
        self.password = password or os.getenv("AEM_PASSWORD")
        self.csrf_token = None
        
        # Create HTTP client with basic authentication
        self.client = httpx.AsyncClient(
            auth=(self.username, self.password),
            verify=False,  # Set to True in production with proper SSL
            timeout=int(os.getenv("AEM_TIMEOUT")),
            headers={
                "Referer": self.host  # Required by AEM for POST operations
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.fetch_csrf_token()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
    
    async def fetch_csrf_token(self) -> str:
        """Fetch CSRF token from AEM with authentication
        
        Returns:
            str: CSRF token
        """
        try:
            # AEM provides CSRF token at this endpoint
            url = f"{self.host}/libs/granite/csrf/token.json"
            
            # Make authenticated request with username and password
            response = await self.client.get(
                url,
                auth=(self.username, self.password)
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.csrf_token = token_data.get("token")
            logger.info("Successfully fetched CSRF token from AEM")
            return self.csrf_token
            
        except Exception as e:
            logger.warning(f"Failed to fetch CSRF token: {e}. Will use X-Requested-With header as fallback.")
            self.csrf_token = None
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for AEM requests including CSRF token
        
        Returns:
            dict: Headers with CSRF token if available
        """
        headers = {}
        if self.csrf_token:
            headers["CSRF-Token"] = self.csrf_token
        else:
            # Fallback to X-Requested-With if no CSRF token
            headers["X-Requested-With"] = "XMLHttpRequest"
        return headers
    
    async def get_page_content(self, page_path: str) -> Dict[str, Any]:
        """Get page content from AEM"""
        try:
            url = f"{self.host}{page_path}.infinity.json"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            content = response.json()
            logger.info(f"Retrieved page content: {page_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error getting page content from AEM: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test connection to AEM"""
        try:
            url = f"{self.host}/libs/granite/core/content/login.html"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"AEM connection test failed: {e}")
            return False

    async def list_pages(self, site_path: str) -> Dict[str, Any]:
        """
        List all pages and JCR nodes under a specific site path
        
        Args:
            site_path: The AEM site path to list pages from (e.g., /content/commercial/mava-international)
            
        Returns:
            Dictionary containing the JCR content with all child nodes and pages
        """
        try:
            # Use infinity.json to get all child nodes and pages
            url = f"{self.host}{site_path}.infinity.json"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            content = response.json()
            logger.info(f"Retrieved page list from: {site_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error listing pages from AEM site {site_path}: {e}")
            raise

    async def get_asset_content(self, asset_path: str) -> str:
        """Retrieve asset content from AEM DAM"""
        try:
            # Construct the asset URL - assets are served directly from DAM
            asset_url = f"{self.host}/content/dam{asset_path}"
            response = await self.client.get(asset_url)
            
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            logger.error(f"Error retrieving asset: {e}")
            return None

    async def duplicate_page_template(self, source_path: str, destination_parent_path: str, new_page_name: str, new_page_title: str, additional_properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Duplicate a page template from source path to a new location
        
        Args:
            source_path: Full path to the source page/template to duplicate
            destination_parent_path: Parent path where the duplicate will be created
            new_page_name: Name for the new page (used in the path)
            new_page_title: Title for the new page
            additional_properties: Optional additional properties to set on the new page
            
        Returns:
            dict: Result containing success status and new page path
        """
        try:
            logger.info(f"Duplicating page template from {source_path} to {destination_parent_path}/{new_page_name}")
            
            # Use AEM's copy operation
            # AEM provides a copy command that duplicates the entire page structure
            copy_url = f"{self.host}{source_path}"
            
            new_page_path = f"{destination_parent_path}/{new_page_name}"
            
            # Build copy operation data
            copy_data = {
                ":operation": "copy",
                ":dest": new_page_path,
                ":async": "true",
                "_charset_": "utf-8"
            }
            
            # Execute copy operation with CSRF token
            # This returns immediately, AEM processes the copy in background
            response = await self.client.post(copy_url, data=copy_data, headers=self._get_headers())
            response.raise_for_status()
            
            logger.info(f"Successfully copied page to {new_page_path}")
            
            # Update the new page's title and additional properties
            update_data = {
                "jcr:content/jcr:title": new_page_title,
                "_charset_": "utf-8"
            }
            
            # Add any additional properties
            if additional_properties:
                for key, value in additional_properties.items():
                    # Prefix with jcr:content/ if not already prefixed
                    prop_key = key if key.startswith("jcr:content/") else f"jcr:content/{key}"
                    update_data[prop_key] = value
            
            # Update the new page with CSRF token
            update_url = f"{self.host}{new_page_path}"
            update_response = await self.client.post(update_url, data=update_data, headers=self._get_headers())
            update_response.raise_for_status()
            
            logger.info(f"Successfully updated page title and properties for {new_page_path}")
            
            return {
                "success": True,
                "source_path": source_path,
                "new_path": new_page_path,
                "message": f"Successfully duplicated template to {new_page_path}"
            }
            
        except Exception as e:
            logger.error(f"Error duplicating page template: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_path": source_path
            }

# ---- End of AEM Content Authoring Utils Functions ----


# ---- Experience Fragment Creation Functions ----

async def create_experience_fragments(aem_client: 'AEMClient', market: str, base_xf_path: str = "/content/experience-fragments") -> dict:
    """
    Create experience fragments for a specific market by fetching HTML templates,
    populating them with market data, and uploading them as experience fragments in AEM.
    
    Creates 5 experience fragments: Header, Footer, LoginFooter, Popup, and LoginHeader
    
    Args:
        aem_client: AEM client instance
        market (str): Market code (india, germany, usa, uk, france)
        base_xf_path (str): Base path for experience fragments in AEM
        
    Returns:
        dict: Results of experience fragment creation
    """
    try:
        # Define the 5 experience fragment templates and their asset paths
        xf_templates = {
            "header": {
                "asset_path": "/content/dam/commercial/mava-international/templates/header.html",
                "xf_path": f"{base_xf_path}/{market}/header",
                "title": f"Header - {market.title()}"
            },
            "footer": {
                "asset_path": "/content/dam/commercial/mava-international/templates/footer.html",
                "xf_path": f"{base_xf_path}/{market}/footer",
                "title": f"Footer - {market.title()}"
            },
            "login-footer": {
                "asset_path": "/content/dam/commercial/mava-international/templates/loginfooter.html",
                "xf_path": f"{base_xf_path}/{market}/login-footer",
                "title": f"Login Footer - {market.title()}"
            },
            "popup": {
                "asset_path": "/content/dam/commercial/mava-international/templates/404.html", 
                "xf_path": f"{base_xf_path}/{market}/popup",
                "title": f"Popup - {market.title()}"
            },
            "profile": {
                "asset_path": "/content/dam/commercial/mava-international/templates/profile.html",
                "xf_path": f"{base_xf_path}/{market}/profile",
                "title": f"Profile - {market.title()}"
            }
        }
        
        results = {}
        
        logger.info(f"Creating experience fragments for market: {market}")
        
        # Process each experience fragment
        for xf_name, xf_config in xf_templates.items():
            try:
                logger.info(f"Processing experience fragment: {xf_name}")
                
                # Step 1: Fetch HTML template from AEM assets
                html_template = await aem_client.get_asset_content(xf_config["asset_path"])
                if not html_template:
                    results[xf_name] = {
                        "success": False,
                        "error": f"Template not found: {xf_config['asset_path']}"
                    }
                    continue
                
                # Step 2: Create experience fragment folder structure if needed
                await ensure_xf_folder_exists(aem_client, f"{base_xf_path}/{market}")
                
                # Step 3: Create the experience fragment
                xf_created = await create_experience_fragment(
                    aem_client,
                    xf_config["xf_path"],
                    xf_config["title"],
                    html_template,
                    xf_name
                )
                
                if xf_created:
                    results[xf_name] = {
                        "success": True,
                        "path": xf_config["xf_path"],
                        "title": xf_config["title"]
                    }
                    logger.info(f"Successfully created experience fragment: {xf_name} at {xf_config['xf_path']}")
                else:
                    results[xf_name] = {
                        "success": False,
                        "error": f"Failed to create experience fragment: {xf_name}"
                    }
                    
            except Exception as e:
                logger.error(f"Error creating experience fragment {xf_name}: {e}")
                results[xf_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Summary
        successful_count = sum(1 for result in results.values() if result.get("success"))
        total_count = len(xf_templates)
        
        return {
            "success": successful_count == total_count,
            "market": market,
            "results": results,
            "summary": {
                "total": total_count,
                "successful": successful_count,
                "failed": total_count - successful_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating experience fragments for market {market}: {e}")
        return {
            "success": False,
            "market": market,
            "error": str(e)
        }


async def ensure_xf_folder_exists(aem_client: 'AEMClient', folder_path: str) -> bool:
    """Ensure experience fragment folder structure exists in AEM"""
    try:
        # Create folder structure using AEM's folder creation API
        url = f"{aem_client.host}{folder_path}"
        
        # Check if folder already exists
        check_response = await aem_client.client.get(url)
        if check_response.status_code == 200:
            return True
        
        # Create folder if it doesn't exist
        folder_data = {
            "jcr:primaryType": "sling:Folder",
            "jcr:title": folder_path.split("/")[-1].title(),
            "_charset_": "utf-8"
        }
        
        response = await aem_client.client.post(url, data=folder_data)
        return response.status_code in [200, 201]
        
    except Exception as e:
        logger.error(f"Error ensuring folder exists {folder_path}: {e}")
        return False


async def create_experience_fragment(aem_client: 'AEMClient', xf_path: str, title: str, html_content: str, fragment_type: str) -> bool:
    """Create an individual experience fragment in AEM"""
    try:
        # Experience fragment structure for AEM
        xf_data = {
            "jcr:primaryType": "cq:Page",
            "jcr:content/jcr:primaryType": "cq:PageContent",
            "jcr:content/sling:resourceType": "cq/experience-fragments/editor/components/experiencefragment",
            "jcr:content/jcr:title": title,
            "jcr:content/cq:template": "/conf/global/settings/wcm/templates/experience-fragment-web-variation",
            "jcr:content/cq:cloudserviceconfigs": ["/etc/cloudservices/contexthub"],
            
            # Master variation
            "jcr:content/data/jcr:primaryType": "nt:unstructured",
            "jcr:content/data/master/jcr:primaryType": "nt:unstructured",
            "jcr:content/data/master/sling:resourceType": "cq/experience-fragments/editor/components/experiencefragment/master",
            "jcr:content/data/master/jcr:title": f"{title} Master",
            
            # Root container
            "jcr:content/data/master/root/jcr:primaryType": "nt:unstructured",
            "jcr:content/data/master/root/sling:resourceType": "wcm/foundation/components/responsivegrid",
            
            # HTML component
            f"jcr:content/data/master/root/{fragment_type}/jcr:primaryType": "nt:unstructured",
            f"jcr:content/data/master/root/{fragment_type}/sling:resourceType": "core/wcm/components/text/v2/text",
            f"jcr:content/data/master/root/{fragment_type}/text": html_content,
            f"jcr:content/data/master/root/{fragment_type}/textIsRich": True,
            
            "_charset_": "utf-8"
        }
        
        response = await aem_client.client.post(f"{aem_client.host}{xf_path}", data=xf_data)
        return response.status_code in [200, 201]
        
    except Exception as e:
        logger.error(f"Error creating experience fragment {xf_path}: {e}")
        return False

# ---- End of Experience Fragment Creation Functions ----
