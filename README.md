# WebVerse Content Authoring API

A Python FastAPI backend for Adobe AEM content authoring and specialized page creation with market-specific content.

## Features

- **Specialized Page Creation**: Create error pages, protected pages, login pages, and HCP modal popups
- **Template Management**: Duplicate and customize page templates for different markets and drugs
- **AEM Integration**: Direct integration with Adobe AEM through REST APIs
- **Health Monitoring**: Comprehensive health checks for AEM connectivity
- **RESTful API**: Clean, documented REST API with OpenAPI/Swagger documentation

## Project Structure

```
WebVerse_Content_Authoring/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── content.py      # Content management endpoints
│   │       │   ├── sites.py        # Site management endpoints
│   │       │   └── health.py       # Health check endpoints
│   │       └── api.py              # API router configuration
│   ├── core/
│   │   ├── config.py               # Application configuration
│   │   ├── database.py             # Database setup and utilities
│   │   └── logging.py              # Logging configuration
│   ├── models/
│   │   ├── content.py              # Content database models
│   │   ├── site.py                 # Site database models
│   │   └── user.py                 # User database models
│   ├── schemas/
│   │   ├── content.py              # Content Pydantic schemas
│   │   ├── site.py                 # Site Pydantic schemas
│   │   └── user.py                 # User Pydantic schemas
│   └── services/
│       └── aem_client.py           # AEM HTTP client service
├── tests/
│   ├── conftest.py                 # Test configuration
│   └── test_main.py                # Basic tests
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (or SQLite for development)
- Adobe AEM instance (for integration)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd WebVerse_Content_Authoring
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   copy .env.example .env
   # Edit .env file with your configuration
   ```

5. **Configure your environment**:
   Edit the `.env` file with your specific configuration:
   - Database connection details
   - AEM instance information
   - Security settings
   - **JCR Service User** (recommended for production)

### Authentication Configuration

#### Option 1: Basic Authentication (Development)

For development environments, you can use basic authentication:

```env
AEM_USE_SERVICE_USER=False
AEM_USERNAME=admin
AEM_PASSWORD=admin
```

#### Option 2: JCR Service User (Production - Recommended)

For production environments, use JCR service user authentication for better security:

```env
# Enable service user authentication
AEM_USE_SERVICE_USER=True
AEM_SERVICE_USER_NAME=content-authoring-service
AEM_SERVICE_USER_SUB_SERVICE=content-writer
AEM_SERVICE_TOKEN_PATH=/path/to/service/user/token.txt
AEM_SERVICE_USER_MAPPING=com.mycompany.content:content-writer=content-authoring-service
```

**Setting up JCR Service User in AEM:**

1. **Create Service User in AEM**:
   ```bash
   # Access AEM User Admin Console
   # Navigate to: http://localhost:4502/security/users.html
   
   # Or use curl to create service user
   curl -u admin:admin -FcreateUser= \
        -FauthorizableId=content-authoring-service \
        -Fprofile/givenName="Content Authoring Service" \
        http://localhost:4502/libs/granite/security/post/authorizables
   ```

2. **Configure Service User Mapping** (OSGi Configuration):
   Create a configuration file at:
   `/apps/myproject/config/org.apache.sling.serviceusermapping.impl.ServiceUserMapperImpl.amended-content.xml`
   
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <jcr:root xmlns:sling="http://sling.apache.org/jcr/sling/1.0" xmlns:jcr="http://www.jcp.org/jcr/1.0"
       jcr:primaryType="sling:OsgiConfig"
       user.mapping="[com.mycompany.content:content-writer=content-authoring-service]"/>
   ```

3. **Grant Permissions to Service User**:
   - Navigate to: `http://localhost:4502/useradmin`
   - Select the service user
   - Go to "Permissions" tab
   - Grant necessary permissions:
     - `jcr:read` on `/content`
     - `jcr:write` on `/content/commercial`
     - `rep:write` on content paths
     - `jcr:nodeTypeManagement` for creating pages

4. **Generate Service Token** (if using token-based auth):
   ```bash
   # Generate and save token
   curl -u admin:admin http://localhost:4502/libs/granite/csrf/token.json > /path/to/service/user/token.txt
   ```

### Database Setup

This application does not require a database. All content is managed directly in Adobe AEM.

## Running the Application

### Supported Markets

The application currently supports the following markets:
- **India** (`india`)
- **Germany** (`germany`)
- **USA** (`usa`)
- **United Kingdom** (`uk`)
- **France** (`france`)

### Supported Page Types

1. **Error Pages**: 404 and 500 error pages with market-specific content
2. **Protected Pages**: Authenticated pages requiring user login (e.g., home, resources, therapeutic information)
3. **Login Pages**: Login pages with multiple HTML components (header, form, footer)
4. **HCP Modal Popups**: Healthcare professional identification modals
5. **Template Duplicates**: Empty page templates customized for market region and drug combinations

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, you can access:

- **Interactive API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Content Authoring Endpoints

#### Error Pages
- `POST /api/v1/content/create-error-pages` - Update existing 404 and 500 error pages with custom JCR content

**Request Body:**
```json
{
  "site_path": "/content/commercial/mava-international/hcp-india/en_us",
  "jcr_content_404": {
    "jcr:primaryType": "cq:Page",
    "jcr:content/jcr:primaryType": "cq:PageContent",
    "jcr:content/jcr:title": "404 Error Page",
    "jcr:content/sling:resourceType": "foundation/components/page",
    "jcr:content/root/jcr:primaryType": "nt:unstructured",
    "jcr:content/root/text/text": "<h1>Page Not Found</h1>"
  },
  "jcr_content_500": {
    "jcr:primaryType": "cq:Page",
    "jcr:content/jcr:primaryType": "cq:PageContent",
    "jcr:content/jcr:title": "500",
    "jcr:content/sling:resourceType": "foundation/components/page",
    "jcr:content/root/jcr:primaryType": "nt:unstructured",
    "jcr:content/root/text/text": "<h1>Internal Server Error</h1>"
  }
}
```

**Features:**
- Automatically extracts market from site path (format: `.../hcp-{market}/...`)
- **Updates** existing error pages at:
  - `{site_path}/error-404-{market}`
  - `{site_path}/error-500-{market}`
- Both `jcr_content_404` and `jcr_content_500` are **required**
- Directly replaces page content with provided JCR structure
- Pages must already exist in AEM

#### Protected Pages
- `POST /api/v1/content/protected-pages` - Create multiple protected/authenticated pages with market-specific content
- `POST /api/v1/content/protected-pages/single` - Create a single protected page

**Multiple Protected Pages Request:**
```json
{
  "site_path": "/content/commercial/mava-international/hcp-india/en_us",
  "market": "india",
  "pages_config": [
    {
      "template_path": "/templates/home.html",
      "page_name": "home",
      "page_title": "Home"
    },
    {
      "template_path": "/templates/resources.html",
      "page_name": "resources",
      "page_title": "Resources"
    }
  ]
}
```

**Single Protected Page Request:**
```json
{
  "site_path": "/content/commercial/mava-international/hcp-india/en_us",
  "market": "india",
  "template_asset_path": "/templates/home.html",
  "page_name": "home",
  "page_title": "Home"
}
```

#### HCP Modal Popup
- `POST /api/v1/content/create-hcp-modal-popup` - Create HCP identification modal popup with market-specific content

**Request Body:**
```json
{
  "site_path": "/content/commercial/mava-international/hcp-india/en_us",
  "market": "india",
  "template_asset_path": "/templates/hcp-modal-popup.html"
}
```

#### Login Page
- `POST /api/v1/content/create-login-page` - Create login page with multiple HTML components (no experience fragments)

**Request Body:**
```json
{
  "site_path": "/content/commercial/mava-international/hcp-india/en_us",
  "market": "india",
  "login_components_config": [
    {
      "component_name": "header",
      "template_path": "/templates/login-header.html"
    },
    {
      "component_name": "form",
      "template_path": "/templates/login-form.html"
    },
    {
      "component_name": "footer",
      "template_path": "/templates/login-footer.html"
    }
  ]
}
```

### Site Management Endpoints

- `POST /api/v1/sites/test-connection` - Test AEM connection with provided credentials
- `GET /api/v1/sites/info` - Get AEM site information including available templates and components
- `GET /api/v1/sites/components` - Get available AEM components
- `GET /api/v1/sites/templates` - Get available AEM page templates
- `POST /api/v1/sites/duplicate-template` - Duplicate the empty page template for a market region and drug

**Duplicate Template Request:**
```json
{
  "market_region": "India",
  "drug": "Aspirin",
  "source_path": "/content/commercial/mava-international/mava-template"
}
```

**Note:** The `source_path` field is required and must specify the template path to duplicate from.

**Duplicate Template Response:**
```json
{
  "success": true,
  "message": "Successfully duplicated template for India - Aspirin",
  "source_template_path": "/content/commercial/mava-international/mava-template",
  "new_template_path": "/content/commercial/mava-international/india-aspirin",
  "market_region": "India",
  "drug": "Aspirin"
}
```

**Features:**
- Duplicates from: Configurable source path (specified in request)
- Creates new page at: `/content/commercial/mava-international/{market_region}-{drug}`
- Stores market region and drug as page properties
- Sanitizes inputs for valid page names

### Health Monitoring

- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/aem` - AEM connection and authentication health check
- `GET /api/v1/health/service-user` - JCR service user authentication status

**AEM Health Check Response:**
```json
{
  "status": "healthy",
  "aem": "connected",
  "host": "http://localhost:4502",
  "authentication": {
    "method": "service_user",
    "status": "authenticated",
    "service_user_valid": true,
    "service_user": "content-authoring-service"
  }
}
```

**Service User Status Response:**
```json
{
  "enabled": true,
  "authenticated": true,
  "valid": true,
  "service_user": "content-authoring-service",
  "sub_service": "content-writer",
  "host": "http://localhost:4502"
}
```

## Configuration

### Environment Variables

Key environment variables you need to configure:

```env
# AEM Basic Configuration
AEM_HOST=http://your-aem-instance:4502
AEM_AUTHOR_URL=http://your-aem-instance:4502
AEM_TIMEOUT=30

# Basic Authentication (Development)
AEM_USERNAME=your-aem-username
AEM_PASSWORD=your-aem-password

# JCR Service User Authentication (Production - Recommended)
AEM_USE_SERVICE_USER=True
AEM_SERVICE_USER_NAME=content-authoring-service
AEM_SERVICE_USER_SUB_SERVICE=content-writer
AEM_SERVICE_TOKEN_PATH=/path/to/service/user/token.txt
AEM_SERVICE_USER_MAPPING=com.mycompany.content:content-writer=content-authoring-service
```

See `.env.example` for the complete list of configuration options.

## Template Requirements

### Template Storage

Templates should be stored in AEM DAM at:
- `/content/dam/commercial/mava-international/templates/`

Example template paths:
- `/content/dam/commercial/mava-international/templates/404.html`
- `/content/dam/commercial/mava-international/templates/500.html`
- `/content/dam/commercial/mava-international/templates/home.html`
- `/content/dam/commercial/mava-international/templates/hcp-modal-popup.html`

## Usage Examples

### Creating Error Pages

```python
import requests

# Create 404 and 500 error pages for a market
error_pages_data = {
    "site_path": "/content/commercial/mava-international/hcp-india/en_us"
}

response = requests.post(
    "http://localhost:8000/api/v1/content/create-error-pages",
    json=error_pages_data
)
print(response.json())
```

### Creating Protected Pages

```python
import requests

# Create multiple protected pages
protected_pages_data = {
    "site_path": "/content/commercial/mava-international/hcp-india/en_us",
    "market": "india",
    "pages_config": [
        {
            "template_path": "/templates/home.html",
            "page_name": "home",
            "page_title": "Home"
        },
        {
            "template_path": "/templates/resources.html",
            "page_name": "resources",
            "page_title": "Resources"
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/content/protected-pages",
    json=protected_pages_data
)
print(response.json())
```

### Creating HCP Modal Popup

```python
import requests

# Create HCP modal popup
popup_data = {
    "site_path": "/content/commercial/mava-international/hcp-india/en_us",
    "market": "india",
    "template_asset_path": "/templates/hcp-modal-popup.html"
}

response = requests.post(
    "http://localhost:8000/api/v1/content/create-hcp-modal-popup",
    json=popup_data
)
print(response.json())
```

### Creating Login Page

```python
import requests

# Create login page with components
login_page_data = {
    "site_path": "/content/commercial/mava-international/hcp-india/en_us",
    "market": "india",
    "login_components_config": [
        {
            "component_name": "header",
            "template_path": "/templates/login-header.html"
        },
        {
            "component_name": "form",
            "template_path": "/templates/login-form.html"
        }
    ]
}

response = requests.post(
    "http://localhost:8000/api/v1/content/create-login-page",
    json=login_page_data
)
print(response.json())
```

### Duplicating Page Template

```python
import requests

# Duplicate empty template for a market and drug
# Example 1: Using standard mava template
duplicate_data = {
    "market_region": "India",
    "drug": "Aspirin",
    "source_path": "/content/commercial/mava-international/mava-template"
}

response = requests.post(
    "http://localhost:8000/api/v1/sites/duplicate-template",
    json=duplicate_data
)
print(response.json())
# Output: {"success": true, "new_template_path": "/content/commercial/mava-international/india-aspirin", ...}

# Example 2: Using a custom source path
duplicate_data_custom = {
    "market_region": "Germany",
    "drug": "Ibuprofen",
    "source_path": "/content/commercial/custom-template"
}

response = requests.post(
    "http://localhost:8000/api/v1/sites/duplicate-template",
    json=duplicate_data_custom
)
print(response.json())
```

### Testing AEM Connection

```python
import requests

# Test AEM connection
test_data = {
    "name": "Test Site",
    "aem_host": "http://localhost:4502",
    "aem_username": "admin",
    "aem_password": "admin",
    "aem_site_path": "/content/mysite"
}

response = requests.post(
    "http://localhost:8000/api/v1/sites/test-connection",
    json=test_data
)
print(response.json())
```

## Testing

Run the test suite:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **isort** for import sorting

Format code:

```bash
black app tests
isort app tests
flake8 app tests
```

### Adding New Features

1. Create appropriate models in `app/models/`
2. Define Pydantic schemas in `app/schemas/`
3. Implement API endpoints in `app/api/v1/endpoints/`
4. Add business logic to `app/services/`
5. Write tests in `tests/`

## Architecture

The application follows a clean architecture pattern:

- **API Layer** (`app/api/`): FastAPI endpoints and request/response handling
- **Business Logic** (`app/services/`): Core business logic, AEM integration, and page creation services
- **Schemas** (`app/schemas/`): Request/response validation and serialization using Pydantic
- **Core** (`app/core/`): Configuration, logging

### Key Services

- **`aem_utils.py`**: AEM client for API communication and template processing
- **`create_error_pages.py`**: Error page (404/500) creation service
- **`create_protected_pages.py`**: Protected/authenticated page creation service
- **`create_popup_pages.py`**: HCP modal popup creation service
- **`create_login_pages.py`**: Login page creation service with multiple components

### Page Creation Workflow

1. **Fetch Template**: Retrieve HTML template from AEM DAM
2. **Create Page**: Upload content to AEM with proper structure
3. **Return Results**: Provide detailed success/failure information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Quick Reference

### API Base URL
- Development: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Common Paths
- **Source Template**: `/content/commercial/mava-international/mava-template`
- **Template Storage**: `/content/dam/commercial/mava-international/templates/`
- **Site Base Path**: `/content/commercial/mava-international/`

### Supported Markets
`india`, `germany`, `usa`, `uk`, `france`

### Available Endpoints Summary
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/content/create-error-pages` | POST | Create 404 & 500 error pages |
| `/api/v1/content/protected-pages` | POST | Create multiple protected pages |
| `/api/v1/content/protected-pages/single` | POST | Create single protected page |
| `/api/v1/content/create-hcp-modal-popup` | POST | Create HCP modal popup |
| `/api/v1/content/create-login-page` | POST | Create login page |
| `/api/v1/sites/duplicate-template` | POST | Duplicate empty template |
| `/api/v1/sites/test-connection` | POST | Test AEM connection |
| `/api/v1/sites/info` | GET | Get site information |
| `/api/v1/sites/components` | GET | Get available components |
| `/api/v1/sites/templates` | GET | Get available templates |
| `/api/v1/health/` | GET | Basic health check |
| `/api/v1/health/aem` | GET | AEM health check |

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on the repository or contact the development team.
