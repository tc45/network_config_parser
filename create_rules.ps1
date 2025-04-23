$rule1 = @"
# Network Configuration Parser - Overview

This project is a network device configuration parser that extracts and analyzes configuration data from various network devices.

## Current Structure
- [main.py](mdc:main.py): Entry point for the CLI application
- [apps/cisco_if_parser.py](mdc:apps/cisco_if_parser.py): Parses Cisco IOS/NXOS configurations
- [apps/asa_parser.py](mdc:apps/asa_parser.py): Parses Cisco ASA firewall configurations
- [apps/palo_alto.py](mdc:apps/palo_alto.py): Parses Palo Alto firewall configurations
- [apps/identify.py](mdc:apps/identify.py): Identifies device types from config files

## Future Direction
The project will evolve into a Django web application with:
- Multi-user collaboration with authentication and authorization
- Customer and project management
- Database storage for parsed configurations
- Comparison between configuration versions
- Extended device support
- Direct SSH connectivity and API integration

## Implementation Plans
- [docs/FUTURE/future_changes.md](mdc:docs/FUTURE/future_changes.md): High-level roadmap
- [docs/FUTURE/detailed_implementation_plan.md](mdc:docs/FUTURE/detailed_implementation_plan.md): Detailed implementation plan
- [docs/FUTURE/implementation_plan.md](mdc:docs/FUTURE/implementation_plan.md): Phase-by-phase implementation approach
"@

$rule2 = @"
# Django Web Application Transition

## Technology Stack
Key technologies for the Django implementation:

- Django Rest Framework (DRF): For exposing parsing functionality via APIs
- HTMX: For reactive UI elements without full SPA complexity
- Django Admin + Tailwind CSS: For admin interface and modern responsive UI
- Celery: For background processing of large config files and scheduled tasks
- Pydantic: For data validation with clean Django ORM integration

## Project Structure
The Django project will follow this structure:
- `NetPrism/` - Django project root
  - `core/` - Main application module
  - `users/` - User authentication and profiles
  - `customers/` - Customer management
  - `projects/` - Project management 
  - `devices/` - Device management
  - `parsers/` - Parser modules with ntc-templates integration

## Core Models
Key database models will include:
- User (extending Django's AbstractUser)
- Customer (organizations using the system)
- Project (collections of devices for specific purposes)
- Device (network hardware being managed)
- DeviceIteration (specific configuration snapshots)
- Various data models (interfaces, routing, ACLs, etc.)

## Implementation Phases
The transition will follow the phases outlined in [docs/FUTURE/implementation_plan.md](mdc:docs/FUTURE/implementation_plan.md):
1. Project Setup and Initial Framework
2. Parser Implementation
3. Django Web Interface
4. Advanced Features
5. Testing and Refinement
"@

$rule3 = @"
# Parser Architecture

## Technology Stack
Technology stack for parser implementation:

- ntc-templates: Core parsing library replacing custom regex
- Pydantic: Data validation and standardization across vendors
- Django ORM: Data persistence with proper model integration
- Celery: Background processing for large files
- DRF: API endpoints for parser functionality

## Current Architecture
The current parser implementation:
- Uses CiscoConfParse2 for Cisco devices
- Has custom parsing logic for different device types
- Extracts data from show tech files using regex patterns
- Outputs data to Excel files or console tables
- Operates as a CLI tool with manual file selection

## Future Architecture
The future parser will:
- Use ntc-templates for standardized parsing
- Implement Pydantic models for data validation
- Store parsed data in a database for persistence and comparison
- Support multiple iterations (versions) of device configurations
- Provide a web interface for data visualization
- Enable direct device connectivity via SSH and APIs

## Parser Integration
The parser integration will include:
- Adapter classes for different device types
- Command mappers for extracting specific outputs
- Transformation utilities for standardizing data formats
- Background processing for handling large files
- Progress tracking and notification
"@

$rule4 = @"
# UI and Dashboard Features

## Frontend Technology Stack
Frontend technology stack:

- Tailwind CSS: Modern responsive styling
- HTMX: Reactive UI components without SPA complexity
- Django Templates: Core templating with HTMX integration
- DataTables: Interactive data visualization for network data
- Chart.js/D3.js: Visual representations of network topology

## Dashboard Overview
The application will feature a responsive dashboard with:
- Summary statistics (customers, projects, devices)
- Recent activity feed
- Quick access to common actions
- Navigation sidebar/header
- Customer and project overview sections

## Data Visualization
Device data will be visualized through:
- Tabbed interfaces for different data types
- Interactive tables with filtering and sorting
- Side-by-side comparison views for config versions
- Highlighting of differences between iterations
- Visual indicators for status (up/down, compliant/non-compliant)

## Customer & Project Management
The interface will include:
- Customer listing and detail views
- Project management within customers
- User association and role management
- Audit logging for changes
- Filtering and search capabilities

## Device Data Views
Device data will be presented with:
- Overview of device information
- Interface configuration details
- Routing information
- Access control lists
- NAT configurations
- VPN settings
- Neighbor discovery information
"@

$rule5 = @"
# Advanced Features

This rule outlines the advanced features planned for the Django network configuration application.

## SSH Connectivity
The application will support direct device connectivity via SSH:
- Netmiko integration for device connections
- Secure credential storage and management
- Command template system for different device types
- Automated data collection from live devices
- Scheduled collection for regular configuration backups

## API Integration
API integration will be implemented for cloud-managed platforms:
- API clients for platforms like Meraki, Cisco DNA Center
- Secure API key management
- Data transformation from API responses to internal models
- Configuration interface for API endpoints
- Rate limiting and error handling

## Data Comparison System
A comprehensive comparison system will allow users to:
- Compare different iterations of the same device
- Compare configurations across different devices
- Highlight differences with visual indicators
- Filter comparisons to focus on specific aspects
- Export comparison results for documentation

## File Upload System
The file upload system will include:
- Progress tracking for file processing
- Background task processing with Celery
- Secure file storage management
- Device type detection from uploaded files
- Integration with the parser system

## Multi-user Collaboration
Collaboration features will enable team-based work:
- Sharing of devices, projects, and customers between users
- Comments and annotations on configurations
- Activity tracking for audit purposes
- Notifications for important changes
- Role-based access controls for sensitive operations
"@

$rule6 = @"
# Implementation and Testing Strategy

This rule outlines the testing and implementation approach for the Django network configuration application.

## Testing Framework
The application will use a comprehensive testing approach:
- Unit tests for all components using pytest
- Integration tests for end-to-end flows
- UI tests using Selenium
- Performance testing for large datasets
- Security testing for authentication and data protection

## Test Fixtures and Factories
The testing infrastructure will include:
- Sample device configuration files for all supported vendors
- Test fixtures and factories for database objects
- Mocking for external services and connections
- Coverage reporting to ensure complete test coverage

## Example Test Cases
```python
# Test user registration
def test_user_registration():
    response = client.post('/accounts/register/', {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'complex_password',
        'password2': 'complex_password',
    })
    assert response.status_code == 302  # Redirect after registration
    assert User.objects.filter(username='testuser').exists()

# Test parsing show interfaces output
def test_parse_show_interfaces():
    with open('tests/sample_data/cisco_ios_show_interfaces.txt', 'r') as f:
        output = f.read()
    
    result = parse_device_output(platform='cisco_ios', command='show interfaces', output=output)
    assert len(result) > 0
    assert 'interface' in result[0]
```

## CI/CD Pipeline
The application will be supported by a CI/CD pipeline:
- Automated testing on each commit
- Code quality checks (flake8, black, isort)
- Security vulnerability scanning
- Automated deployment to staging environment
- Production deployment process

## Implementation Phases
The implementation will follow the phased approach in [docs/FUTURE/implementation_plan.md](mdc:docs/FUTURE/implementation_plan.md):
1. Project Setup and Initial Framework
2. Parser Implementation
3. Django Web Interface
4. Advanced Features
5. Testing and Refinement
"@

$rule7 = @"
# Current Codebase Structure and Evolution

This rule outlines the current codebase structure and how it will evolve into the Django application.

## Current Structure
The current CLI application consists of:
- [main.py](mdc:main.py): Entry point that handles file selection and parser orchestration
- [apps/identify.py](mdc:apps/identify.py): Device type identification from configuration files
- [apps/cisco_if_parser.py](mdc:apps/cisco_if_parser.py): Parser for Cisco IOS/NXOS devices
- [apps/asa_parser.py](mdc:apps/asa_parser.py): Parser for Cisco ASA firewalls
- [apps/palo_alto.py](mdc:apps/palo_alto.py): Parser for Palo Alto devices
- [apps/utils.py](mdc:apps/utils.py): General utility functions
- [apps/exporter.py](mdc:apps/exporter.py): Handles export to Excel spreadsheets
- [apps/netmiko_util.py](mdc:apps/netmiko_util.py): Netmiko integration for SSH connectivity

## Code Evolution
Current components will evolve as follows:

### Device Identification
- Current: Simple regex pattern matching in [apps/identify.py](mdc:apps/identify.py)
- Future: Enhanced identification with ntc-templates platform detection

### Cisco Parser
- Current: Complex regex-based parsing in [apps/cisco_if_parser.py](mdc:apps/cisco_if_parser.py)
- Future: Simpler adapter using ntc-templates with standardized data models

### ASA Parser
- Current: Custom parser in [apps/asa_parser.py](mdc:apps/asa_parser.py)
- Future: ntc-templates integration with specialized ASA adapters

### Palo Alto Parser
- Current: Custom parsing in [apps/palo_alto.py](mdc:apps/palo_alto.py)
- Future: Streamlined with standardized data models and API integration

### Export Functionality
- Current: Direct Excel export in [apps/exporter.py](mdc:apps/exporter.py)
- Future: Flexible export system with multiple formats and templates

## Implementation Strategy
The implementation will follow a progressive enhancement approach:
1. Create Django project structure with core models
2. Refactor existing parsers to use ntc-templates
3. Implement database storage and web interface
4. Add advanced features while maintaining backward compatibility
"@

# First, remove any existing rules
Remove-Item -Force .cursor\rules\*.mdc -ErrorAction SilentlyContinue

# Create or update the rules
Set-Content -Path ".cursor\rules\01-project-overview.mdc" -Value $rule1
Set-Content -Path ".cursor\rules\02-django-transition.mdc" -Value $rule2
Set-Content -Path ".cursor\rules\03-parser-architecture.mdc" -Value $rule3
Set-Content -Path ".cursor\rules\04-ui-dashboard.mdc" -Value $rule4
Set-Content -Path ".cursor\rules\05-advanced-features.mdc" -Value $rule5
Set-Content -Path ".cursor\rules\06-implementation-testing.mdc" -Value $rule6
Set-Content -Path ".cursor\rules\07-current-codebase.mdc" -Value $rule7

Write-Host "Rules files created successfully!" 