# NetPrism: Network Configuration Parser and Analyzer

## Project Overview

NetPrism is a Django-based web application for parsing, analyzing, and managing network device configurations. It supports various network devices including Cisco IOS/IOS-XE/NXOS, Cisco ASA firewalls, and Palo Alto firewalls. The application extracts configuration elements from show-tech outputs and organizes them into structured data that can be easily analyzed, compared, and visualized.

### Key Goals

1. **Modernize the Existing Parser**: Transform the current script-based solution into a robust Django web application
2. **Improve User Experience**: Create an intuitive interface for uploading, parsing, and analyzing configurations
3. **Enhance Analysis Capabilities**: Provide deeper insights through visualizations and comparison features
4. **Multi-tenant Support**: Allow organizations to manage their own devices, configurations, and users
5. **Version Control**: Track configuration changes over time and provide diff capabilities
6. **API Integration**: Enable programmatic access to parsing and analysis features

## Technical Stack

- **Backend Framework**: Django 4.x
- **Database**: PostgreSQL
- **Package Management**: Poetry
- **Frontend**: HTML, CSS (Bootstrap/Tailwind), JavaScript
- **Authentication**: Django authentication system with custom user model
- **Testing**: pytest, Django test framework
- **Deployment**: Docker, Docker Compose

## Project Directory Structure

```
netprism/
├── .github/                      # GitHub workflows and templates
├── .vscode/                      # VSCode configuration
├── src/                          # Source code directory
│   ├── apps/                     # Django applications
│   │   ├── core/                 # Core functionality and shared utilities
│   │   │   ├── management/       # Django management commands
│   │   │   ├── migrations/       # Database migrations
│   │   │   ├── templatetags/     # Custom template tags
│   │   │   └── utils/            # Utility functions
│   │   ├── users/                # User authentication and profiles
│   │   ├── customers/            # Customer and project management
│   │   ├── devices/              # Device management
│   │   ├── parsers/              # Parsing functionality
│   │   │   ├── cisco/            # Cisco-specific parsers
│   │   │   ├── asa/              # ASA-specific parsers
│   │   │   └── palo_alto/        # Palo Alto-specific parsers
│   │   └── dashboard/            # Dashboard views and reports
│   ├── config/                   # Django project configuration
│   │   ├── settings/             # Environment-specific settings
│   │   ├── urls.py               # URL routing
│   │   └── wsgi.py               # WSGI application
│   ├── docs/                     # Documentation
│   │   ├── FUTURE/               # Future development plans
│   │   └── api/                  # API documentation
│   ├── input/                    # Input files for processing
│   ├── logs/                     # Application logs
│   ├── output/                   # Parser output files
│   ├── static/                   # Static files (CSS, JS, images)
│   ├── templates/                # HTML templates
│   ├── tests/                    # Test suite
│   └── manage.py                 # Django management script
├── README.md                     # Project README
├── pyproject.toml                # Poetry project configuration
├── .gitignore                    # Git ignore rules
├── docker-compose.yml            # Docker Compose configuration
├── Dockerfile                    # Docker build configuration
├── .env.example                  # Example environment variables
└── manage.py                     # Root manage.py (redirects to src/manage.py)
```

## Implementation Phases

### Phase 1: Project Setup and Infrastructure

1. Initialize Poetry and project structure
2. Set up Django project and apps
3. Configure database and authentication
4. Implement deployment setup with Docker

### Phase 2: Core Feature Development

1. Port existing parsers to the Django application
2. Develop file upload and management system
3. Create parser execution framework
4. Implement basic reporting and data views

### Phase 3: Advanced Features and User Interface

1. Develop dashboard and visualization components
2. Implement configuration comparison and version tracking
3. Create customer and project management functionality
4. Build user management and permissions system

### Phase 4: API and Integration

1. Design and implement REST API
2. Develop integration with external systems
3. Create documentation and client examples
4. Implement background task processing

## Validation Criteria

For each implementation step, the following validation criteria should be applied:

1. **Code Quality**: Passes linting and follows PEP 8 standards
2. **Test Coverage**: Has appropriate unit and integration tests
3. **Documentation**: Includes docstrings and user documentation
4. **Performance**: Meets performance requirements for the given feature
5. **Security**: Follows security best practices and passes security review
6. **UX Testing**: For UI features, passes usability testing

## Current Status

The project is transitioning from a script-based solution to a Django web application. The current code has working parsers for various device types, but lacks the web interface, multi-tenancy, and advanced features planned for NetPrism.

### Existing Components

- Parser modules for Cisco IOS/NXOS, ASA, and Palo Alto devices
- Utility functions for output formatting and file handling
- Basic CLI interface for running parsers

### Next Steps

1. Complete the Poetry project setup
2. Initialize the Django project structure
3. Migrate existing parsers to the Django application
4. Implement the core user interface components 