# Detailed Implementation Plan

This document provides a comprehensive, step-by-step guide for implementing the Network Configuration Parser Django application. Each section includes:

1. **Description**: What we're building and why
2. **AI Prompt**: Text you can copy/paste to instruct the AI assistant
3. **Implementation Steps**: Specific actions to complete
4. **Deliverables**: Expected outputs to validate completion
5. **Validation Tests**: How to verify the component works correctly

## Table of Contents

1. [Project Setup](#1-project-setup)
2. [Core Models](#2-core-models)
3. [Authentication System](#3-authentication-system)
4. [Parser Integration](#4-parser-integration)
5. [Data Modeling](#5-data-modeling)
6. [File Upload System](#6-file-upload-system)
7. [Basic Dashboard](#7-basic-dashboard)
8. [Customer & Project Management](#8-customer--project-management)
9. [Device Data Visualization](#9-device-data-visualization)
10. [Data Comparison System](#10-data-comparison-system)
11. [Export System](#11-export-system)
12. [SSH Connectivity](#12-ssh-connectivity)
13. [API Integration](#13-api-integration)
14. [Containerization](#14-containerization)
15. [Testing & Quality Assurance](#15-testing--quality-assurance)

---

## 1. Project Setup

### Description
Set up the initial Django project with Poetry/UV for dependency management, configure directory structure, and set up the base settings.

### 1.1. Poetry Project Initialization

#### Description
Initialize the Poetry project with basic configuration and dependencies.

#### AI Prompt
```
I need to initialize a Poetry project for our network configuration parser application. Please:

1. Create a pyproject.toml file with Poetry configuration
2. Set up Python 3.10+ as the requirement
3. Add Django 4.2+ as the main dependency
4. Add other essential dependencies:
   - django-environ (for environment variables)
   - psycopg2-binary (for PostgreSQL support)
   - python-decouple (for settings configuration)
   - whitenoise (for static file handling)
5. Configure development dependencies:
   - pytest
   - pytest-django
   - black
   - isort
   - flake8

Please include git commit instructions to version control this initial setup.
```

#### Implementation Steps
1. Create Poetry project with `poetry init`
2. Configure Python version requirement
3. Add Django and other dependencies
4. Set up development dependencies
5. Git init, add .gitignore file, and make initial commit

#### Deliverables
- pyproject.toml file with dependencies
- .gitignore file with Python/Django patterns
- Initial git repository with first commit

#### Validation Tests
1. Run `poetry install` to verify dependencies install correctly
2. Check Python version compatibility
3. Verify that git repository is properly initialized

### 1.2. Django Project Creation

#### Description
Create the base Django project structure with the core app.

#### AI Prompt
```
Now that Poetry is set up, I need to create the Django project structure for our network configuration parser application. Please:

1. Create a Django project called "netprism"
2. Create the following Django apps:
   - core (for shared models and utilities)
   - users (for user authentication and profiles)
   - customers (for customer and project management)
   - devices (for device management)
   - parsers (for parsing functionality)
   - dashboard (for dashboard views)
3. Configure the apps with appropriate __init__.py, apps.py, etc.
4. Set up a logical directory structure
5. Update INSTALLED_APPS setting

Please include git commit instructions to track these changes.
```

#### Implementation Steps
1. Create Django project: `poetry run django-admin startproject netprism .`
2. Create core app: `poetry run python manage.py startapp core`
3. Create additional apps: users, customers, devices, parsers, dashboard
4. Organize apps in proper directory structure
5. Update each app's configuration files

#### Deliverables
- Django project structure
- Multiple app directories
- Updated settings.py with installed apps
- Git commit capturing the project creation

#### Validation Tests
1. Run `poetry run python manage.py check` to verify the project structure
2. Verify all apps are properly registered
3. Check that imports work correctly

### 1.3. Settings Configuration

#### Description
Configure Django settings.py with environment variables, database settings, and other configurations.

#### AI Prompt
```
I need to configure the settings.py file for our Django network configuration parser application. Please:

1. Set up python-decouple for environment variable management
2. Create development settings using SQLite
3. Allow for PostgreSQL configuration in production
4. Configure static and media file handling
5. Set up sensible defaults for Django settings
6. Create a .env.example file as a template
7. Configure logging

Additionally, set up the project to use different settings for development and production environments. Please include git commit instructions.
```

#### Implementation Steps
1. Configure environment variable handling
2. Set up development database settings
3. Create production database settings
4. Configure static/media files
5. Set up logging
6. Create separate settings modules for different environments

#### Deliverables
- Updated settings.py with environment variable support
- Development and production settings configurations
- .env.example file
- Configured static/media file handling
- Git commit with settings changes

#### Validation Tests
1. Run `poetry run python manage.py check` to validate settings
2. Create a .env file and test loading environment variables
3. Verify database connection works

### 1.4. Base URL Configuration

#### Description
Set up URL routing for the project and apps.

#### AI Prompt
```
I need to configure the URL routing for our Django network configuration parser application. Please:

1. Set up the main urls.py file with proper namespacing
2. Create empty urls.py files for each app
3. Configure a basic URL pattern for the dashboard
4. Set up static/media URL handling
5. Configure proper URL namespacing for apps

Please include git commit instructions to save these changes.
```

#### Implementation Steps
1. Configure main urls.py
2. Create urls.py in each app
3. Set up proper URL namespacing
4. Configure static/media URL handling
5. Create basic URL routes for initial views

#### Deliverables
- Configured main urls.py
- URL modules for each app
- Basic routing structure
- Git commit with URL configuration

#### Validation Tests
1. Run `poetry run python manage.py check` to validate URL configuration
2. Verify that URLs are properly namespaced
3. Test that URL reversing works correctly

### 1.5. Base Templates and Static Files

#### Description
Set up templates directory, base templates, and static files structure.

#### AI Prompt
```
I need to set up the base templates and static files for our Django network configuration parser application. Please:

1. Create a templates directory structure
2. Create a base.html template with common structure
3. Set up static files directories for CSS, JS, and images
4. Add bootstrap or tailwind for styling
5. Set up basic JavaScript libraries
6. Create a simple landing page template

Please include git commit instructions to track these changes.
```

#### Implementation Steps
1. Create templates directory structure
2. Set up base.html with common elements
3. Create static files structure
4. Add CSS/JS libraries
5. Create basic templates for landing page

#### Deliverables
- Templates directory with base templates
- Static files structure
- CSS/JS library integration
- Simple landing page template
- Git commit with template/static setup

#### Validation Tests
1. Run development server to check template rendering
2. Verify static files are properly loaded
3. Test responsiveness on different screen sizes

### 1.6. Project Documentation

#### Description
Create initial project documentation including README.md and setup instructions.

#### AI Prompt
```
I need to create the initial documentation for our Django network configuration parser application. Please:

1. Create a comprehensive README.md with:
   - Project overview
   - Setup instructions
   - Development workflow
   - Basic usage information
2. Create a CONTRIBUTING.md with contribution guidelines
3. Set up documentation structure for further docs
4. Create installation instructions for different environments

Please include git commit instructions to save these documents.
```

#### Implementation Steps
1. Create README.md with project overview
2. Add setup and installation instructions
3. Create CONTRIBUTING.md for contribution guidelines
4. Set up documentation structure

#### Deliverables
- Comprehensive README.md
- CONTRIBUTING.md
- Documentation structure
- Git commit with documentation

#### Validation Tests
1. Verify README.md contains complete setup instructions
2. Test the setup instructions to ensure they work
3. Verify all links in documentation work correctly

---

## 2. Core Models

### Description
Implement the core data models for the application, including User, Customer, Project, Device, and related models.

### 2.1. Base Abstract Models

#### Description
Create abstract base models with common functionality for use across the application.

#### AI Prompt
```
I need to create abstract base models for our Django network configuration parser application. Please:

1. Create a TimeStampedModel with:
   - created_at field
   - updated_at field
   - appropriate Meta options
2. Create a BaseModel with:
   - UUID primary key
   - TimeStampedModel inheritance
   - String representation method
3. Create an AuditableModel with:
   - created_by field (ForeignKey to User)
   - updated_by field (ForeignKey to User)
   - appropriate signals or methods to track changes

These models should be in the core app and used as base classes for other models. Please include git commit instructions.
```

#### Implementation Steps
1. Create abstract base models in core/models.py
2. Implement TimeStampedModel
3. Implement BaseModel with UUID
4. Create AuditableModel with user tracking

#### Deliverables
- Abstract base models in core/models.py
- Proper Meta options on all models
- String representation methods
- Git commit with base models

#### Validation Tests
1. Run `python manage.py makemigrations` to check for errors
2. Create a test model inheriting from BaseModel
3. Verify timestamps are automatically set
4. Test audit tracking functionality

### 2.2. User Models

#### Description
Implement user-related models including custom User model and profile.

#### AI Prompt
```
I need to implement the user-related models for our Django network configuration parser application. Please:

1. Create a custom User model extending AbstractUser with:
   - Email as the primary identifier (optional)
   - Additional fields as needed
   - Proper string representation
2. Create a UserProfile model with:
   - One-to-one relationship with User
   - Profile picture field
   - Job title and department fields
   - Contact information fields
3. Create a Role model for role-based access control
4. Create appropriate signals for profile creation

These models should be in the users app. Please include git commit instructions.
```

#### Implementation Steps
1. Create custom User model in users/models.py
2. Implement UserProfile model
3. Create Role model for RBAC
4. Set up signals for automatic profile creation

#### Deliverables
- Custom User model
- UserProfile model with needed fields
- Role model for permissions
- Migration files
- Git commit with user models

#### Validation Tests
1. Run `python manage.py makemigrations users`
2. Run `python manage.py check` for model validation
3. Create a test user and verify profile is created
4. Test relationships between User, Profile, and Roles

### 2.3. Customer and Project Models

#### Description
Implement customer and project-related models.

#### AI Prompt
```
I need to implement the customer and project models for our Django network configuration parser application. Please:

1. Create a Customer model with:
   - name, description fields
   - contact information fields
   - status field (active, inactive, etc.)
   - Custom manager for common queries
2. Create a Project model with:
   - ForeignKey to Customer
   - name, description fields
   - status and type fields
   - start_date and end_date fields
3. Create UserCustomer and UserProject association models
   - Many-to-many through with custom fields
   - Role field (admin, viewer, etc.)
   - Include timestamp fields
4. Add appropriate indexes for performance

These models should be in the customers app. Please include git commit instructions.
```

#### Implementation Steps
1. Create Customer model in customers/models.py
2. Create Project model with customer relationship
3. Implement association models for permissions
4. Add custom manager for common queries
5. Create database indexes for performance

#### Deliverables
- Customer model
- Project model
- Association models for permissions
- Migration files
- Git commit with customer/project models

#### Validation Tests
1. Run `python manage.py makemigrations customers`
2. Test creating customers and projects
3. Test user-customer-project relationships
4. Verify permission associations work correctly

### 2.4. Device Models

#### Description
Implement device-related models for storing network device information.

#### AI Prompt
```
I need to implement the device-related models for our Django network configuration parser application. Please:

1. Create a Device model with:
   - Basic fields (hostname, vendor, platform, model, serial_number, etc.)
   - ForeignKey to Project
   - Management IP and credentials fields (with proper encryption)
   - Status and type fields
   - Last seen and uptime fields
2. Create a DeviceType model for categorization
3. Create a DeviceIteration model for tracking changes:
   - ForeignKey to Device
   - Source information (file, API, SSH)
   - Timestamp and user information
   - Status of processing
4. Add appropriate indexes and constraints

These models should be in the devices app. Please include git commit instructions.
```

#### Implementation Steps
1. Create Device model in devices/models.py
2. Create DeviceType model for categorization
3. Implement DeviceIteration model for change tracking
4. Add indexes and constraints for performance

#### Deliverables
- Device model
- DeviceType model
- DeviceIteration model
- Migration files
- Git commit with device models

#### Validation Tests
1. Run `python manage.py makemigrations devices`
2. Test creating devices and device iterations
3. Verify relationships work correctly
4. Test encryption of sensitive fields

### 2.5. Parser Data Models

#### Description
Implement models for storing parsed network device data.

#### AI Prompt
```
I need to implement the parser data models for our Django network configuration parser application. Please:

1. Create base abstract model for parsed data with:
   - ForeignKey to DeviceIteration
   - Common fields for all parsed data
2. Create specific models for different data types:
   - InterfaceData (name, status, IP, etc.)
   - RoutingData (protocol, network, next-hop, etc.)
   - ACLData (name, rules, etc.)
   - VLANData (id, name, ports, etc.)
   - Additional models as needed
3. Use JSONField where appropriate for flexible data storage
4. Add appropriate indexes for query performance
5. Include string representations and Meta options

These models should be in the parsers app. Please include git commit instructions.
```

#### Implementation Steps
1. Create base abstract model for parsed data
2. Implement specific models for each data type
3. Add appropriate fields and relationships
4. Create indexes for performance
5. Add Meta options and string methods

#### Deliverables
- Base abstract model for parsed data
- Specific models for different data types
- Migration files
- Git commit with parser data models

#### Validation Tests
1. Run `python manage.py makemigrations parsers`
2. Create test data for each model
3. Test relationships with devices and iterations
4. Verify query performance with indexes

### 2.6. Admin Site Configuration

#### Description
Configure Django admin site for all models.

#### AI Prompt
```
I need to configure the Django admin site for our network configuration parser application models. Please:

1. Create ModelAdmin classes for all models with:
   - Appropriate list_display fields
   - Filtering and search capabilities
   - Custom actions where useful
   - Inline editing for related models
2. Customize admin forms with:
   - Fieldsets for logical grouping
   - Readonly fields where appropriate
   - Custom validation
3. Set up proper registration of all models
4. Add custom admin templates where needed

Please include git commit instructions.
```

#### Implementation Steps
1. Create admin.py files for each app
2. Configure ModelAdmin classes
3. Set up inlines for related models
4. Add custom actions and forms
5. Register all models with admin site

#### Deliverables
- Configured admin.py for each app
- Custom ModelAdmin classes
- Admin templates where needed
- Git commit with admin configuration

#### Validation Tests
1. Run development server and access admin site
2. Test CRUD operations for each model
3. Verify filters and search functionality
4. Test custom actions

### 2.7. API Serializers for Core Models

#### Description
Create DRF serializers for core models to enable API functionality.

#### AI Prompt
```
I need to create Django REST Framework serializers for our core models. Please:

1. Add django-rest-framework as a dependency
2. Create serializers for:
   - User and UserProfile models
   - Customer and Project models
   - Device and DeviceIteration models
   - Parsed data models
3. Include nested serialization where appropriate
4. Add validation methods
5. Create serializer mixins for common functionality
6. Set up hyperlinked relationships where useful

Please include git commit instructions.
```

#### Implementation Steps
1. Add DRF dependency
2. Create serializers.py for each app
3. Implement model serializers
4. Add validation methods
5. Set up proper relationships

#### Deliverables
- DRF dependency added to pyproject.toml
- Serializers for all core models
- Validation methods
- Git commit with serializers

#### Validation Tests
1. Run `python manage.py check` to verify serializers
2. Test serialization of model instances
3. Verify validation logic works
4. Test nested serialization

---

## 3. Authentication System

### Description
Implement user authentication, registration, permissions, and role-based access control.

### 3.1. Basic Authentication Setup

#### Description
Configure the base authentication system using Django's built-in authentication.

#### AI Prompt
```
I need to set up the basic authentication system for our Django network configuration parser application. Please:

1. Configure Django's authentication backend
2. Set up login, logout, and password reset URLs
3. Configure email backend for auth emails
4. Add necessary settings for authentication
5. Set up password validators
6. Configure session handling

Please include git commit instructions for these changes.
```

#### Implementation Steps
1. Configure AUTH_USER_MODEL setting
2. Set up authentication backends
3. Configure password validators
4. Set up email backend for auth emails
5. Configure session settings

#### Deliverables
- Configured authentication settings
- Email backend setup
- Password validation configuration
- Session handling settings
- Git commit with auth configuration

#### Validation Tests
1. Run `python manage.py check` to verify configuration
2. Test email sending configuration
3. Verify session settings

### 3.2. User Registration System

#### Description
Implement user registration functionality with email verification.

#### AI Prompt
```
I need to implement a user registration system with email verification for our Django application. Please:

1. Create registration forms with:
   - Username, email, password fields
   - Custom validation logic
   - Terms acceptance field
2. Implement registration views with:
   - Form handling
   - Email verification sending
   - Success/error message handling
3. Create email verification system:
   - Secure token generation
   - Verification endpoint
   - Expiration handling
4. Create templates for:
   - Registration form
   - Email verification emails
   - Success/failure pages

Please include git commit instructions.
```

#### Implementation Steps
1. Create custom registration forms
2. Implement registration views
3. Set up email verification logic
4. Create templates for registration and verification
5. Configure URLs for registration flow

#### Deliverables
- Registration forms
- Registration views
- Email verification system
- Templates for registration process
- Git commit with registration system

#### Validation Tests
1. Test user registration with valid/invalid data
2. Verify email verification flow
3. Test edge cases (expired tokens, duplicate registrations)
4. Check form validation

### 3.3. Login and Session Management

#### Description
Implement login, logout, and session management functionality.

#### AI Prompt
```
I need to implement login, logout, and session management for our Django application. Please:

1. Create custom login view and form with:
   - Username/email and password fields
   - Remember me functionality
   - Failed login attempt tracking
   - CSRF protection
2. Implement logout functionality
3. Create session management:
   - Session timeout settings
   - Active session listing
   - Session termination ability
4. Develop templates for:
   - Login page
   - Session management page
   - Logout confirmation

Please include git commit instructions.
```

#### Implementation Steps
1. Create custom login form
2. Implement login view with security features
3. Set up logout functionality
4. Implement session management features
5. Create templates for login/logout

#### Deliverables
- Login form and view
- Logout view
- Session management functionality
- Templates for authentication
- Git commit with login/session system

#### Validation Tests
1. Test login with valid/invalid credentials
2. Verify remember me functionality
3. Test session timeout and management
4. Check security features (CSRF, brute force protection)

### 3.4. Password Management

#### Description
Implement password reset, change, and management functionality.

#### AI Prompt
```
I need to implement password management functionality for our Django application. Please:

1. Set up password reset flow:
   - Request form with email validation
   - Secure token generation
   - Reset form with validation
   - Success/failure handling
2. Create password change functionality:
   - Current password verification
   - New password with confirmation
   - Password strength validation
3. Implement password expiration policy
4. Create templates for:
   - Password reset request
   - Password reset emails
   - Password reset form
   - Password change form

Please include git commit instructions.
```

#### Implementation Steps
1. Set up password reset views and forms
2. Create password change functionality
3. Implement password policy features
4. Create templates for password management
5. Configure URLs for password management

#### Deliverables
- Password reset functionality
- Password change views and forms
- Password policy implementation
- Templates for password management
- Git commit with password management

#### Validation Tests
1. Test password reset flow end-to-end
2. Verify password change functionality
3. Test password policy enforcement
4. Check security measures

### 3.5. Role-Based Access Control

#### Description
Implement role-based access control (RBAC) system.

#### AI Prompt
```
I need to implement a role-based access control system for our Django application. Please:

1. Define role models and permissions:
   - Admin, Manager, Viewer base roles
   - Custom permission logic
   - Role hierarchy
2. Create role assignment views:
   - User-role association
   - Role editing
   - Permission management
3. Implement access control:
   - Permission-checking decorators
   - Template-level permission checks
   - API permission classes
4. Create permission middleware:
   - Request-level permission checking
   - Role-based content filtering

Please include git commit instructions.
```

#### Implementation Steps
1. Define role and permission models
2. Create role assignment views and forms
3. Implement permission-checking decorators
4. Create permission middleware
5. Add template-level permission checks

#### Deliverables
- Role and permission models
- Role management interface
- Permission decorators and middleware
- Template tags for permissions
- Git commit with RBAC system

#### Validation Tests
1. Test role assignment functionality
2. Verify permission checks work correctly
3. Test role hierarchy enforcement
4. Check permission-based content filtering

### 3.6. User-Customer-Project Permissions

#### Description
Implement user permissions for customers and projects.

#### AI Prompt
```
I need to implement a permission system for user access to customers and projects. Please:

1. Create association models:
   - UserCustomer with role field
   - UserProject with role field
   - Include timestamps and metadata
2. Implement permission views:
   - User assignment to customers/projects
   - Role management for assignments
   - Bulk assignment capabilities
3. Create permission checking:
   - Middleware for request filtering
   - Decorators for view protection
   - Template tags for UI customization
4. Implement UI for permission management

Please include git commit instructions.
```

#### Implementation Steps
1. Create association models with roles
2. Implement permission assignment views
3. Create permission checking utilities
4. Develop UI for permission management
5. Set up middleware for request filtering

#### Deliverables
- UserCustomer and UserProject models
- Permission assignment interface
- Permission checking utilities
- UI for permission management
- Git commit with permission system

#### Validation Tests
1. Test assigning users to customers/projects
2. Verify permission checks work correctly
3. Test permission-based content filtering
4. Check UI elements based on permissions

### 3.7. User Profile Management

#### Description
Implement user profile management functionality.

#### AI Prompt
```
I need to implement user profile management for our Django application. Please:

1. Create profile views:
   - Profile display view
   - Profile edit form
   - Password change integration
   - Profile picture upload
2. Implement profile features:
   - Notification preferences
   - UI theme/preferences
   - Time zone selection
   - API key management
3. Create templates for:
   - Profile display
   - Profile editing
   - Preferences management
4. Set up URL routing for profile management

Please include git commit instructions.
```

#### Implementation Steps
1. Create profile display and edit views
2. Implement profile feature management
3. Create templates for profile management
4. Set up URL routing for profile pages
5. Add profile picture handling

#### Deliverables
- Profile management views
- Profile edit forms
- Preference management
- Profile templates
- Git commit with profile management

#### Validation Tests
1. Test profile editing functionality
2. Verify preference saving
3. Test profile picture upload
4. Check user-specific settings

### 3.8. Authentication Testing

#### Description
Create comprehensive tests for authentication system.

#### AI Prompt
```
I need to create comprehensive tests for our Django authentication system. Please:

1. Implement unit tests for:
   - User registration
   - Login/logout functionality
   - Password reset/change
   - Permission checks
   - Role assignments
2. Create integration tests for:
   - Complete authentication flows
   - Session management
   - Email verification
3. Implement test fixtures:
   - Test users with different roles
   - Test customers and projects
   - Permission setups
4. Add performance tests for permission checking

Please include git commit instructions.
```

#### Implementation Steps
1. Create test fixtures for auth testing
2. Write unit tests for auth components
3. Implement integration tests for flows
4. Set up performance tests
5. Create test documentation

#### Deliverables
- Test fixtures for authentication
- Unit tests for auth components
- Integration tests for auth flows
- Performance test suite
- Git commit with auth tests

#### Validation Tests
1. Run the test suite and verify all tests pass
2. Check test coverage report
3. Verify edge cases are covered
4. Test performance under load

---

## 4. Parser Integration

### Description
Integrate ntc-templates library for parsing network device outputs, create adapter classes, and implement command extractors.

### 4.1. NTC-Templates Integration

#### Description
Set up the core ntc-templates integration for parsing network device outputs.

#### AI Prompt
```
I need to integrate the ntc-templates library for parsing network device outputs in our Django application. Please:

1. Add ntc-templates as a dependency in Poetry
2. Create a parser service module in the parsers app
3. Implement base parsing functionality:
   - Template discovery and loading
   - Text parsing using TextFSM
   - Result formatting and validation
4. Add tests for basic parsing functionality
5. Create documentation for supported templates

Please include git commit instructions.
```

#### Implementation Steps
1. Add ntc-templates as a dependency
2. Create a parser service module
3. Implement template loading functionality
4. Set up core parsing methods
5. Create sample parser tests

#### Deliverables
- Updated dependencies with ntc-templates
- Parser service module
- Core parsing functionality
- Basic test suite
- Git commit with ntc-templates integration

#### Validation Tests
1. Test loading and discovering templates
2. Verify basic parsing works with sample data
3. Check error handling for invalid inputs
4. Run the parser test suite

### 4.2. Command Extraction Utilities

#### Description
Create utilities for extracting specific command outputs from show tech files.

#### AI Prompt
```
I need to create utilities for extracting command outputs from show tech files for network devices. Please:

1. Implement command extraction:
   - Regex patterns for common command prompts
   - Section extraction logic
   - Multi-vendor support
   - Nested command handling
2. Create utility functions:
   - File loading and preprocessing
   - Command identification
   - Output cleaning and normalization
3. Add test cases with:
   - Sample show tech files
   - Expected extraction results
   - Edge case handling
4. Document the extraction patterns and logic

Please include git commit instructions.
```

#### Implementation Steps
1. Create module for command extraction
2. Implement regex patterns for commands
3. Create utility functions for processing
4. Add test cases with sample files
5. Document the extraction logic

#### Deliverables
- Command extraction module
- Utility functions for processing
- Test cases with sample files
- Documentation for extraction patterns
- Git commit with command extraction utilities

#### Validation Tests
1. Test extraction on sample show tech files
2. Verify command identification accuracy
3. Check edge case handling
4. Measure performance on large files

### 4.3. Device Type Identification

#### Description
Implement logic to identify device types from configuration output.

#### AI Prompt
```
I need to implement device type identification logic for network configuration files. Please:

1. Create identification module:
   - Signature patterns for different vendors/models
   - Version extraction logic
   - OS and firmware identification
   - Platform mapping to ntc-templates format
2. Implement identification strategies:
   - Prompt-based identification
   - Command output analysis
   - Banner parsing
   - Fallback mechanisms
3. Add comprehensive tests with:
   - Sample outputs from different devices
   - Edge cases and partial outputs
   - Performance benchmarking
4. Create mappings for supported device types

Please include git commit instructions.
```

#### Implementation Steps
1. Create device identification module
2. Implement signature patterns for devices
3. Create identification strategies
4. Add mapping to ntc-templates platforms
5. Create comprehensive test suite

#### Deliverables
- Device identification module
- Signature patterns for different devices
- Identification strategies
- Platform mapping to ntc-templates
- Git commit with device identification

#### Validation Tests
1. Test identification on sample device outputs
2. Verify version extraction accuracy
3. Check mapping to ntc-templates platform names
4. Test with partial or ambiguous outputs

### 4.4. Vendor-Specific Adapters

#### Description
Create adapter classes for different vendor platforms.

#### AI Prompt
```
I need to create vendor-specific adapter classes for parsing network device configurations. Please:

1. Design adapter interface:
   - Common methods for all adapters
   - Abstract base class
   - Registration mechanism
2. Implement vendor-specific adapters:
   - Cisco IOS/NXOS adapter
   - Cisco ASA adapter
   - Palo Alto adapter
   - Arista EOS adapter
   - Juniper adapter
3. Add specialized parsing logic:
   - Command mapping for each vendor
   - Output normalization
   - Error handling
4. Create factory class for adapter selection

Please include git commit instructions.
```

#### Implementation Steps
1. Create adapter interface and base class
2. Implement vendor-specific adapters
3. Add specialized parsing logic
4. Create adapter factory class
5. Add registration mechanism

#### Deliverables
- Adapter interface and base class
- Vendor-specific adapter implementations
- Specialized parsing logic
- Adapter factory class
- Git commit with vendor adapters

#### Validation Tests
1. Test each adapter with sample configurations
2. Verify command mapping accuracy
3. Check error handling for each adapter
4. Test adapter factory selection logic

### 4.5. Command Mapping Configuration

#### Description
Create configuration files and logic for mapping between commands and templates.

#### AI Prompt
```
I need to create command mapping configurations for our network device parser. Please:

1. Design command mapping structure:
   - YAML or JSON configuration files
   - Vendor and platform organization
   - Command to template mappings
   - Parameter specifications
2. Implement mapping loading and validation:
   - Configuration file loading
   - Schema validation
   - Fallback and default mappings
3. Create mappings for key platforms:
   - Cisco IOS command mappings
   - Cisco NXOS command mappings
   - Cisco ASA command mappings
   - Palo Alto command mappings
4. Add documentation for extending mappings

Please include git commit instructions.
```

#### Implementation Steps
1. Design command mapping structure
2. Create configuration files for mappings
3. Implement mapping loading and validation
4. Create mappings for key platforms
5. Add documentation

#### Deliverables
- Command mapping structure
- Configuration files for different platforms
- Mapping loading and validation code
- Documentation for extending mappings
- Git commit with command mappings

#### Validation Tests
1. Validate mapping configuration files
2. Test loading mappings for different platforms
3. Verify template references are valid
4. Check fallback behavior

### 4.6. Parser Service Implementation

#### Description
Create a comprehensive parser service for processing network device outputs.

#### AI Prompt
```
I need to implement a comprehensive parser service for network device outputs. Please:

1. Create parser service architecture:
   - Service class design
   - Asynchronous processing support
   - Plugin architecture for extensibility
   - Caching mechanism
2. Implement core parsing functionality:
   - Device identification
   - Command extraction
   - Template selection and parsing
   - Result normalization
3. Add error handling and logging:
   - Structured error reporting
   - Detailed logging
   - Fallback mechanisms
4. Create parsing pipeline with stages

Please include git commit instructions.
```

#### Implementation Steps
1. Design parser service architecture
2. Implement core parsing functionality
3. Add error handling and logging
4. Create parsing pipeline with stages
5. Implement caching mechanism

#### Deliverables
- Parser service architecture
- Core parsing implementation
- Error handling and logging
- Parsing pipeline
- Git commit with parser service

#### Validation Tests
1. Test end-to-end parsing with sample data
2. Verify error handling with invalid inputs
3. Check logging and error reporting
4. Measure parsing performance and caching

### 4.7. Parser Result Transformation

#### Description
Create utilities for transforming parser results into standard data formats.

#### AI Prompt
```
I need to create transformation utilities for parser results. Please:

1. Design transformation system:
   - Adapter pattern for different formats
   - Pipeline for multi-stage transformations
   - Configuration options
2. Implement transformers for:
   - Raw parser output to internal models
   - Cross-vendor normalization
   - Data enrichment and validation
3. Create utility functions:
   - Field mapping and renaming
   - Type conversion
   - Format standardization
4. Add validation for transformed data

Please include git commit instructions.
```

#### Implementation Steps
1. Design transformation system
2. Implement transformers for different outputs
3. Create utility functions
4. Add validation for transformed data
5. Document transformation process

#### Deliverables
- Transformation system design
- Transformer implementations
- Utility functions
- Validation logic
- Git commit with transformation utilities

#### Validation Tests
1. Test transformations with sample parser outputs
2. Verify cross-vendor normalization
3. Check data validation and error handling
4. Test complex transformation pipelines

### 4.8. Parser Integration Testing

#### Description
Create comprehensive tests for the parser integration.

#### AI Prompt
```
I need to create comprehensive tests for our network device parser integration. Please:

1. Set up test fixtures:
   - Sample device outputs for each platform
   - Expected parsing results
   - Edge case samples
2. Implement test suites:
   - Unit tests for parser components
   - Integration tests for end-to-end flows
   - Performance tests for large files
3. Create test utilities:
   - Result comparison helpers
   - Test data generators
   - Mock services
4. Document testing approach and coverage

Please include git commit instructions.
```

#### Implementation Steps
1. Create test fixtures with sample data
2. Implement unit tests for parser components
3. Create integration tests for end-to-end flows
4. Add performance tests
5. Document testing approach

#### Deliverables
- Test fixtures with sample data
- Unit test suite
- Integration test suite
- Performance tests
- Git commit with parser tests

#### Validation Tests
1. Run the complete test suite
2. Verify test coverage
3. Check edge case handling
4. Measure performance metrics

### 4.9. Template Management System

#### Description
Implement a system for users and admins to view, edit, share, and version control custom ntc-templates.

#### AI Prompt
```
I need to implement a template management system for ntc-templates in our network configuration parser application. Please:

1. Create a template management model structure:
   - Template model (vendor, OS, command, content, version)
   - Template ownership (user, admin, global)
   - Template sharing settings (private, specific users, global)
   - Version tracking fields
2. Implement template CRUD functionality:
   - Import from ntc-templates GitHub repository
   - Template editor with syntax highlighting
   - Version control for changes
   - Diff comparison between versions
3. Add sharing and permissions system:
   - User-specific templates
   - Admin-managed templates
   - Sharing with specific users
   - Global availability setting
4. Create the template selection system:
   - Environment variable management for NTC_TEMPLATES_DIR
   - Priority selection logic (user templates > shared templates > admin templates > default templates)
   - Template directory synchronization

Please include git commit instructions and ensure templates are properly versioned.
```

#### Implementation Steps
1. Set up GitHub integration to fetch ntc-templates
2. Create template models with ownership and sharing
3. Implement template editor with version control
4. Add sharing and permissions system
5. Create template selection and directory management
6. Implement environment variable configuration

#### Deliverables
- Template management models
- Template CRUD functionality
- Version control system
- Template sharing permissions
- Editor with syntax highlighting
- Templates directory management
- Git commit with template management system

#### Validation Tests
1. Test importing templates from GitHub
2. Verify template editing and version control
3. Test sharing permissions and visibility
4. Check template selection priority logic
5. Verify environment variable configuration works

---

## 5. Data Modeling

### Description
Create Pydantic models for standardizing and validating parsed data, with transformers to convert between formats.

### 5.1. Pydantic Setup and Base Models

#### Description
Set up Pydantic and create base models for data validation.

#### AI Prompt
```
I need to set up Pydantic and create base models for our network configuration parser. Please:

1. Add pydantic as a dependency
2. Create base model structure:
   - BaseModel with common functionality
   - Config classes for validation settings
   - Custom validators and types
3. Implement common utilities:
   - JSON serialization/deserialization
   - Field transformations
   - Validation error handling
4. Create documentation for model usage

Please include git commit instructions.
```

#### Implementation Steps
1. Add pydantic dependency
2. Create base model structure
3. Implement common utilities
4. Document model usage
5. Add sample validation

#### Deliverables
- Pydantic dependency added
- Base model structure
- Common utilities
- Documentation
- Git commit with Pydantic setup

#### Validation Tests
1. Test base model validation
2. Verify serialization/deserialization
3. Check error handling
4. Test with sample data

### 5.2. Network Entity Models

#### Description
Create Pydantic models for common network entities.

#### AI Prompt
```
I need to create Pydantic models for common network entities. Please:

1. Implement interface model:
   - Name, description fields
   - Status, speed, duplex
   - IP addressing information
   - VLAN association
   - Physical characteristics
2. Create routing model:
   - Protocol types
   - Network and prefix
   - Next hop information
   - Administrative distance and metrics
3. Implement ACL model:
   - Rule structure
   - Source/destination information
   - Actions and logging
4. Add VLAN model, neighbor model, etc.

Please include git commit instructions.
```

#### Implementation Steps
1. Create interface model
2. Implement routing model
3. Create ACL model
4. Add VLAN and neighbor models
5. Implement additional common models

#### Deliverables
- Interface Pydantic model
- Routing Pydantic model
- ACL Pydantic model
- VLAN and neighbor models
- Git commit with network entity models

#### Validation Tests
1. Test models with valid and invalid data
2. Verify validation logic
3. Check relationships between models
4. Test serialization/deserialization

### 5.3. Vendor-Specific Model Variations

#### Description
Create vendor-specific variations of the base network entity models.

#### AI Prompt
```
I need to create vendor-specific variations of our network entity models. Please:

1. Implement vendor-specific interface models:
   - Cisco IOS interface specifics
   - Cisco NXOS interface specifics
   - Palo Alto interface specifics
   - Other vendor variations
2. Create vendor-specific routing models
3. Implement vendor-specific ACL models
4. Build inheritance hierarchy:
   - Base models for common fields
   - Vendor-specific extensions
   - Platform-specific variations

Please include git commit instructions.
```

#### Implementation Steps
1. Create vendor-specific interface models
2. Implement vendor-specific routing models
3. Create vendor-specific ACL models
4. Build inheritance hierarchy
5. Add validation for vendor-specific fields

#### Deliverables
- Vendor-specific interface models
- Vendor-specific routing models
- Vendor-specific ACL models
- Inheritance hierarchy
- Git commit with vendor-specific models

#### Validation Tests
1. Test with vendor-specific sample data
2. Verify inheritance works correctly
3. Check vendor-specific validation
4. Test conversion between vendor models

### 5.4. Network Data Validators

#### Description
Implement validators for network-specific data types.

#### AI Prompt
```
I need to implement validators for network-specific data types in our Pydantic models. Please:

1. Create IP address validators:
   - IPv4 address validation
   - IPv6 address validation
   - Subnet mask and CIDR validation
   - IP range validation
2. Implement MAC address validators
3. Create interface name validators:
   - Vendor-specific patterns
   - Standard format validation
4. Add VLAN, routing protocol, and other validators

Please include git commit instructions.
```

#### Implementation Steps
1. Create IP address validators
2. Implement MAC address validators
3. Create interface name validators
4. Add additional network validators
5. Document validation logic

#### Deliverables
- IP address validators
- MAC address validators
- Interface name validators
- Additional network validators
- Git commit with network validators

#### Validation Tests
1. Test validators with valid and invalid data
2. Verify error messages are clear
3. Check edge cases
4. Test validation performance

### 5.5. Transformation Utilities

#### Description
Create utilities for transforming between different data formats.

#### AI Prompt
```
I need to create transformation utilities for our network data models. Please:

1. Implement ntc-templates to Pydantic transformers:
   - Mapping functions for each template type
   - Field normalization
   - Type conversion
2. Create Django ORM to Pydantic converters:
   - Model to Pydantic conversion
   - Pydantic to model conversion
   - Relationship handling
3. Add cross-vendor normalization:
   - Field name standardization
   - Value normalization
   - Structure harmonization
4. Implement transformation pipeline

Please include git commit instructions.
```

#### Implementation Steps
1. Create ntc-templates transformers
2. Implement Django ORM converters
3. Add cross-vendor normalization
4. Create transformation pipeline
5. Document transformation process

#### Deliverables
- ntc-templates transformers
- Django ORM converters
- Cross-vendor normalization
- Transformation pipeline
- Git commit with transformation utilities

#### Validation Tests
1. Test transformations with sample data
2. Verify ORM round-trip conversion
3. Check cross-vendor normalization
4. Test transformation performance

### 5.6. Serialization/Deserialization Methods

#### Description
Implement serialization and deserialization methods for different formats.

#### AI Prompt
```
I need to implement serialization and deserialization methods for our network data models. Please:

1. Create JSON serialization:
   - Custom encoders for network types
   - Pretty printing options
   - Schema generation
2. Implement YAML serialization
3. Add CSV serialization:
   - Field selection
   - Header formatting
   - Type conversion
4. Create binary serialization for efficient storage

Please include git commit instructions.
```

#### Implementation Steps
1. Implement JSON serialization
2. Create YAML serialization
3. Add CSV serialization
4. Implement binary serialization
5. Document serialization options

#### Deliverables
- JSON serialization methods
- YAML serialization methods
- CSV serialization methods
- Binary serialization
- Git commit with serialization methods

#### Validation Tests
1. Test serialization with complex data
2. Verify round-trip conversion
3. Check handling of special types
4. Measure serialization performance

### 5.7. Data Model Integration Testing

#### Description
Create comprehensive tests for data modeling components.

#### AI Prompt
```
I need to create comprehensive tests for our data modeling components. Please:

1. Set up test fixtures:
   - Sample data for different models
   - Transformation test cases
   - Serialization examples
2. Implement test suites:
   - Model validation tests
   - Transformation test cases
   - Serialization/deserialization tests
   - Performance benchmarks
3. Create test utilities:
   - Data generators
   - Comparison helpers
   - Benchmark framework
4. Document test coverage and approach

Please include git commit instructions.
```

#### Implementation Steps
1. Create test fixtures with sample data
2. Implement model validation tests
3. Add transformation test cases
4. Create serialization tests
5. Add performance benchmarks

#### Deliverables
- Test fixtures with sample data
- Model validation test suite
- Transformation test cases
- Serialization test suite
- Git commit with data model tests

#### Validation Tests
1. Run the complete test suite
2. Verify test coverage
3. Check edge case handling
4. Measure performance metrics

---

## 6. File Upload System

### Description
Implement a system for uploading, processing, and storing network device configuration files.

### 6.1. File Upload Views and Forms

#### Description
Create views and forms for file uploading.

#### AI Prompt
```
I need to create file upload views and forms for our network configuration parser application. Please:

1. Implement upload forms:
   - File field with validation
   - Metadata fields (name, description, device selection)
   - AJAX support for progress tracking
   - Multiple file selection
2. Create upload views:
   - Form handling
   - Validation logic
   - Security checks
   - Redirect and messaging
3. Add templates:
   - Upload form with drag-and-drop
   - Progress visualization
   - Success/error displays
4. Configure URL routing

Please include git commit instructions.
```

#### Implementation Steps
1. Create file upload forms
2. Implement file upload views
3. Add templates with AJAX support
4. Configure URL routing
5. Implement client-side validation

#### Deliverables
- File upload forms
- Upload views
- Templates with progress tracking
- URL configuration
- Git commit with upload views and forms

#### Validation Tests
1. Test file upload with valid and invalid files
2. Verify progress tracking works
3. Check validation messages
4. Test multiple file uploads

### 6.2. File Validation and Security

#### Description
Implement file validation and security measures.

#### AI Prompt
```
I need to implement file validation and security measures for our file upload system. Please:

1. Create file type validation:
   - MIME type checking
   - File extension validation
   - Content inspection
   - Signature verification
2. Implement security measures:
   - Size limits
   - Rate limiting
   - Virus scanning integration
   - Filename sanitization
3. Add error handling:
   - User-friendly error messages
   - Detailed logging
   - Security alerting
4. Create validation pipeline

Please include git commit instructions.
```

#### Implementation Steps
1. Implement file type validation
2. Create size and rate limiting
3. Add security measures
4. Create validation pipeline
5. Implement error handling

#### Deliverables
- File type validation
- Size and rate limiting
- Security measures
- Validation pipeline
- Git commit with file validation and security

#### Validation Tests
1. Test with various file types
2. Verify size limits are enforced
3. Check security measures
4. Test error messages

### 6.3. Storage Management

#### Description
Implement secure storage management for uploaded files.

#### AI Prompt
```
I need to implement secure storage management for uploaded configuration files. Please:

1. Configure Django storage:
   - Custom storage class
   - Path generation logic
   - Permissions and access control
   - Versioning support
2. Implement file organization:
   - Directory structure
   - Naming conventions
   - Metadata storage
3. Add security features:
   - Encrypted storage option
   - Access logging
   - Expiration and cleanup
4. Create management commands for maintenance

Please include git commit instructions.
```

#### Implementation Steps
1. Configure Django storage backend
2. Implement file organization logic
3. Add security features
4. Create management commands
5. Document storage architecture

#### Deliverables
- Custom storage configuration
- File organization logic
- Security features
- Management commands
- Git commit with storage management

#### Validation Tests
1. Test file storage and retrieval
2. Verify directory structure and organization
3. Check security features
4. Test management commands

### 6.4. Background Task Processing

#### Description
Set up background task processing for file uploads.

#### AI Prompt
```
I need to set up background task processing for file uploads using Celery. Please:

1. Configure Celery:
   - Add dependencies
   - Set up broker (Redis/RabbitMQ)
   - Configure worker settings
   - Create task queues
2. Implement task definitions:
   - File processing task
   - Parser integration
   - Result handling
   - Error management
3. Add progress tracking:
   - Task status updates
   - Progress percentage calculation
   - User notification
4. Create monitoring and management interface

Please include git commit instructions.
```

#### Implementation Steps
1. Add Celery dependencies
2. Configure broker and workers
3. Implement task definitions
4. Add progress tracking
5. Create monitoring interface

#### Deliverables
- Celery configuration
- Task definitions
- Progress tracking
- Monitoring interface
- Git commit with background processing

#### Validation Tests
1. Test task execution
2. Verify progress tracking
3. Check error handling
4. Test monitoring interface

### 6.5. Device Type Detection

#### Description
Implement automatic device type detection from uploaded files.

#### AI Prompt
```
I need to implement automatic device type detection for uploaded configuration files. Please:

1. Create detection service:
   - Integration with parser identification
   - Content sampling and analysis
   - Confidence scoring
   - Fallback mechanisms
2. Implement detection workflow:
   - Pre-processing step
   - Multiple detection strategies
   - Result validation
   - User confirmation interface
3. Add detection results:
   - Metadata storage
   - User interface display
   - Confidence indicators
4. Create manual override mechanism

Please include git commit instructions.
```

#### Implementation Steps
1. Create detection service
2. Implement detection workflow
3. Add result storage and display
4. Create manual override mechanism
5. Document detection algorithms

#### Deliverables
- Detection service
- Detection workflow
- Results storage and display
- Manual override mechanism
- Git commit with device detection

#### Validation Tests
1. Test detection with various device configurations
2. Verify confidence scoring
3. Check fallback mechanisms
4. Test manual override

### 6.6. Parser Integration

#### Description
Integrate file upload system with the parser service.

#### AI Prompt
```
I need to integrate the file upload system with our parser service. Please:

1. Create integration workflow:
   - Automatic parsing after upload
   - Background task creation
   - Database storage of results
   - Error handling
2. Implement result processing:
   - Transform parsed data to models
   - Database storage
   - Relationship creation
   - Metadata updates
3. Add user interface:
   - Status display
   - Results preview
   - Navigation to detailed views
4. Create reprocessing mechanism

Please include git commit instructions.
```

#### Implementation Steps
1. Create integration workflow
2. Implement result processing
3. Add user interface elements
4. Create reprocessing mechanism
5. Document integration points

#### Deliverables
- Integration workflow
- Result processing
- User interface elements
- Reprocessing mechanism
- Git commit with parser integration

#### Validation Tests
1. Test end-to-end upload and parse workflow
2. Verify database storage of results
3. Check error handling
4. Test reprocessing functionality

### 6.7. File Upload System Testing

#### Description
Create comprehensive tests for the file upload system.

#### AI Prompt
```
I need to create comprehensive tests for our file upload system. Please:

1. Implement unit tests:
   - Form validation
   - View functionality
   - Storage mechanisms
   - Parser integration
2. Create integration tests:
   - End-to-end upload workflow
   - Background processing
   - Device detection
   - Result storage
3. Add performance tests:
   - Large file handling
   - Concurrent uploads
   - Processing throughput
4. Create test fixtures and utilities

Please include git commit instructions.
```

#### Implementation Steps
1. Create unit tests for components
2. Implement integration tests
3. Add performance tests
4. Create test fixtures
5. Document testing approach

#### Deliverables
- Unit test suite
- Integration tests
- Performance tests
- Test fixtures
- Git commit with upload system tests

#### Validation Tests
1. Run test suite and verify coverage
2. Check performance metrics
3. Verify error handling tests
4. Test with large sample files

---

## 7. Basic Dashboard

### Description
Create a responsive dashboard interface with navigation, customer overview, and recent activity.

### 7.1. Base Template Setup

#### Description
Create base templates and layout for the dashboard.

#### AI Prompt
```
I need to create base templates and layout for our network configuration dashboard. Please:

1. Design base template structure:
   - HTML5 boilerplate
   - Responsive meta tags
   - CSS framework integration (Bootstrap/Tailwind)
   - Script loading
2. Implement layout components:
   - Header with branding and user menu
   - Responsive navigation sidebar
   - Main content area
   - Footer with info
3. Create blocks for template inheritance:
   - Title, meta, styles
   - Navigation items
   - Content blocks
   - Script blocks
4. Add responsive behavior for mobile/tablet/desktop

Please include git commit instructions.
```

#### Implementation Steps
1. Create base.html template
2. Implement layout components
3. Set up template inheritance blocks
4. Add responsive design
5. Include static assets

#### Deliverables
- Base template structure
- Layout components
- Template inheritance blocks
- Responsive design
- Git commit with base templates

#### Validation Tests
1. Check rendering on different screen sizes
2. Verify template inheritance works
3. Test navigation components
4. Check static asset loading

### 7.2. Navigation System

#### Description
Implement the navigation sidebar/header system.

#### AI Prompt
```
I need to implement a navigation system for our dashboard. Please:

1. Create navigation sidebar:
   - Collapsible sections
   - Icon and text labels
   - Active state indication
   - Permission-based visibility
2. Implement header navigation:
   - User dropdown menu
   - Notifications area
   - Quick actions
   - Search functionality
3. Add breadcrumb navigation:
   - Context-aware breadcrumbs
   - Template tag implementation
   - Schema markup
4. Create mobile-friendly navigation:
   - Responsive behavior
   - Touch-friendly targets
   - Off-canvas menu

Please include git commit instructions.
```

#### Implementation Steps
1. Create navigation sidebar component
2. Implement header navigation
3. Add breadcrumb system
4. Create mobile navigation
5. Add permission-based visibility

#### Deliverables
- Navigation sidebar component
- Header navigation
- Breadcrumb system
- Mobile navigation
- Git commit with navigation system

#### Validation Tests
1. Test navigation on different screen sizes
2. Verify permission-based visibility
3. Check active state indication
4. Test mobile navigation interaction

### 7.3. Dashboard Statistics

#### Description
Implement dashboard statistics and summary components.

#### AI Prompt
```
I need to implement dashboard statistics and summary components. Please:

1. Create statistics service:
   - Data aggregation methods
   - Caching mechanism
   - Asynchronous updates
   - Permission filtering
2. Implement visual components:
   - Card-based statistics
   - Charts and graphs
   - Trend indicators
   - Interactive elements
3. Add the following statistics:
   - Customer and project counts
   - Device statistics by type/vendor
   - Recent activity metrics
   - Health status indicators
4. Create refreshable components with AJAX

Please include git commit instructions.
```

#### Implementation Steps
1. Create statistics service
2. Implement visual components
3. Add specific statistics
4. Create AJAX refresh functionality
5. Add caching for performance

#### Deliverables
- Statistics service
- Visual components
- Dashboard statistics
- AJAX refresh
- Git commit with dashboard statistics

#### Validation Tests
1. Verify statistics accuracy
2. Test caching and performance
3. Check permission filtering
4. Test AJAX refresh functionality

### 7.4. Recent Activity Feed

#### Description
Implement a recent activity feed for the dashboard.

#### AI Prompt
```
I need to implement a recent activity feed for our dashboard. Please:

1. Create activity tracking:
   - Activity model/table
   - Logging middleware
   - Event categorization
   - User and object associations
2. Implement activity display:
   - Chronological feed
   - Filtering options
   - Pagination
   - Real-time updates
3. Add activity types:
   - User actions (login, upload, etc.)
   - System events (parsing completion, etc.)
   - Error notifications
   - User-specific vs. global activities
4. Create notification mechanism

Please include git commit instructions.
```

#### Implementation Steps
1. Create activity tracking models
2. Implement logging middleware
3. Create activity display component
4. Add filtering and pagination
5. Implement real-time updates

#### Deliverables
- Activity tracking models
- Logging middleware
- Activity display component
- Filtering and pagination
- Git commit with activity feed

#### Validation Tests
1. Test activity logging for different actions
2. Verify display and formatting
3. Check filtering and pagination
4. Test real-time updates

### 7.5. Dashboard Views and Controllers

#### Description
Create the main dashboard views and controllers.

#### AI Prompt
```
I need to create the main dashboard views and controllers. Please:

1. Implement dashboard views:
   - Main dashboard view
   - Summary section
   - Recent items section
   - Quick action section
2. Create view controllers:
   - Data aggregation
   - Permission checks
   - Context preparation
   - Response rendering
3. Add URL routing:
   - Dashboard index route
   - Section-specific routes
   - AJAX endpoints
4. Implement view optimization:
   - Query optimization
   - Caching
   - Deferred loading

Please include git commit instructions.
```

#### Implementation Steps
1. Create main dashboard view
2. Implement controllers for data
3. Add URL routing
4. Create context processors
5. Optimize queries and caching

#### Deliverables
- Main dashboard view
- View controllers
- URL routing
- Optimized queries
- Git commit with dashboard views

#### Validation Tests
1. Test dashboard rendering
2. Verify data aggregation
3. Check permission-based content
4. Measure loading performance

### 7.6. Dashboard Customization

#### Description
Implement dashboard customization capabilities.

#### AI Prompt
```
I need to implement dashboard customization capabilities. Please:

1. Create user preferences:
   - Layout preferences
   - Widget visibility
   - Default filters
   - Color scheme selection
2. Implement customization interface:
   - Drag-and-drop widget arrangement
   - Widget settings
   - Save/reset functionality
   - Preview changes
3. Add persistent storage:
   - User preference model
   - Server-side storage
   - Browser cache fallback
4. Create default configurations for roles

Please include git commit instructions.
```

#### Implementation Steps
1. Create user preferences model
2. Implement customization interface
3. Add persistent storage
4. Create default configurations
5. Add preference migration

#### Deliverables
- User preferences model
- Customization interface
- Persistent storage
- Default configurations
- Git commit with dashboard customization

#### Validation Tests
1. Test saving and loading preferences
2. Verify customization interface
3. Check persistence across sessions
4. Test default configurations by role

---

## 8. Customer & Project Management

### Description
Implement interfaces for creating, editing, and managing customers and projects.

### 8.1. Customer CRUD Views

#### Description
Create views for customer management.

#### AI Prompt
```
I need to create CRUD views for customer management. Please:

1. Implement customer list view:
   - Sortable and filterable table
   - Pagination
   - Search functionality
   - Permission-based actions
2. Create customer detail view:
   - Key information display
   - Associated projects list
   - User access list
   - Activity history
3. Add create/edit views:
   - Form with validation
   - File uploads for logos/documents
   - AJAX submission
   - Success/error handling
4. Implement delete functionality:
   - Confirmation dialog
   - Dependency checking
   - Soft delete option

Please include git commit instructions.
```

#### Implementation Steps
1. Create customer list view
2. Implement customer detail view
3. Add create/edit forms and views
4. Create delete functionality
5. Add permission checks

#### Deliverables
- Customer list view
- Customer detail view
- Create/edit forms and views
- Delete functionality
- Git commit with customer CRUD views

#### Validation Tests
1. Test creating, viewing, editing, deleting customers
2. Verify permission checks
3. Test validation rules
4. Check dependency handling for delete

### 8.2. Project CRUD Views

#### Description
Create views for project management.

#### AI Prompt
```
I need to create CRUD views for project management. Please:

1. Implement project list view:
   - Filtering by customer/status
   - Sortable columns
   - Search functionality
   - Quick actions
2. Create project detail view:
   - Summary information
   - Device listing
   - User access list
   - Activity timeline
   - Related documents
3. Add create/edit views:
   - Customer selection
   - Form with validation
   - Document attachments
   - Settings configuration
4. Implement archive/delete functionality

Please include git commit instructions.
```

#### Implementation Steps
1. Create project list view
2. Implement project detail view
3. Add create/edit forms and views
4. Create archive/delete functionality
5. Add permission checks

#### Deliverables
- Project list view
- Project detail view
- Create/edit forms and views
- Archive/delete functionality
- Git commit with project CRUD views

#### Validation Tests
1. Test creating, viewing, editing, archiving projects
2. Verify customer association
3. Test validation rules
4. Check permission enforcement

### 8.3. User Association Management

#### Description
Implement user association management for customers and projects.

#### AI Prompt
```
I need to implement user association management for customers and projects. Please:

1. Create association interface:
   - User selector with search
   - Role assignment dropdown
   - Bulk operations
   - Expiration date option
2. Implement permission management:
   - Role-based permissions
   - Custom permission flags
   - Inheritance options (customer to project)
   - Override capabilities
3. Add user listing views:
   - Users by customer/project
   - Role filtering
   - Access level indicators
   - Last activity information
4. Create self-service request workflow

Please include git commit instructions.
```

#### Implementation Steps
1. Create user association interface
2. Implement permission management
3. Add user listing views
4. Create request workflow
5. Implement inheritance logic

#### Deliverables
- User association interface
- Permission management
- User listing views
- Request workflow
- Git commit with user association management

#### Validation Tests
1. Test adding/removing users
2. Verify role assignment
3. Check permission inheritance
4. Test request workflow

### 8.4. Sharing Functionality

#### Description
Implement sharing capabilities between users.

#### AI Prompt
```
I need to implement sharing functionality for customers and projects. Please:

1. Create sharing interface:
   - User/group selector
   - Permission level selection
   - Duration options
   - Notification toggle
2. Implement sharing backend:
   - Permission grant system
   - Temporary access tokens
   - Expiration handling
   - Audit logging
3. Add notification system:
   - Email notifications
   - In-app notifications
   - Access granted messages
   - Expiration reminders
4. Create shared item views

Please include git commit instructions.
```

#### Implementation Steps
1. Create sharing interface
2. Implement sharing backend
3. Add notification system
4. Create shared item views
5. Add expiration handling

#### Deliverables
- Sharing interface
- Sharing backend
- Notification system
- Shared item views
- Git commit with sharing functionality

#### Validation Tests
1. Test sharing with different permissions
2. Verify notification delivery
3. Check expiration handling
4. Test shared item access

### 8.5. Audit Logging

#### Description
Implement audit logging for customer and project changes.

#### AI Prompt
```
I need to implement audit logging for customer and project changes. Please:

1. Create audit log system:
   - Change tracking model
   - Before/after value capture
   - User and timestamp recording
   - Action categorization
2. Implement logging integration:
   - Model save signals
   - Form submission tracking
   - API request logging
   - Bulk action logging
3. Add audit log interface:
   - Filterable log viewer
   - Change details display
   - Export capability
   - Retention policy
4. Create reporting functionality

Please include git commit instructions.
```

#### Implementation Steps
1. Create audit log models
2. Implement logging integration
3. Add audit log interface
4. Create reporting functionality
5. Configure retention policies

#### Deliverables
- Audit log models
- Logging integration
- Audit log interface
- Reporting functionality
- Git commit with audit logging

#### Validation Tests
1. Test logging for various change types
2. Verify change detail capture
3. Check filtering and searching
4. Test export functionality

### 8.6. Search and Filtering

#### Description
Implement advanced search and filtering capabilities.

#### AI Prompt
```
I need to implement advanced search and filtering capabilities for customers and projects. Please:

1. Create search infrastructure:
   - Full-text search integration
   - Field-specific search
   - Search result highlighting
   - Relevance ranking
2. Implement filtering system:
   - Filter by multiple criteria
   - Saved filter sets
   - Dynamic filter UI
   - Filter combinations
3. Add advanced query capabilities:
   - Complex query building
   - Date range filtering
   - Relational filtering
   - Nested conditions
4. Create search/filter UI components

Please include git commit instructions.
```

#### Implementation Steps
1. Create search infrastructure
2. Implement filtering system
3. Add advanced query capabilities
4. Create UI components
5. Optimize for performance

#### Deliverables
- Search infrastructure
- Filtering system
- Advanced query capabilities
- Search/filter UI components
- Git commit with search and filtering

#### Validation Tests
1. Test search with various queries
2. Verify filter combinations
3. Check performance with large datasets
4. Test saved filters

### 8.7. Reporting and Analytics

#### Description
Implement reporting and analytics for customers and projects.

#### AI Prompt
```
I need to implement reporting and analytics for customers and projects. Please:

1. Create report templates:
   - Customer summary report
   - Project status report
   - Device inventory report
   - Activity and usage report
2. Implement analytics dashboard:
   - Key metrics visualization
   - Trend analysis
   - Comparison charts
   - Drilldown capabilities
3. Add export functionality:
   - PDF report generation
   - Excel data export
   - CSV export
   - Scheduled reports
4. Create custom report builder

Please include git commit instructions.
```

#### Implementation Steps
1. Create report templates
2. Implement analytics dashboard
3. Add export functionality
4. Create report builder
5. Add scheduling capabilities

#### Deliverables
- Report templates
- Analytics dashboard
- Export functionality
- Custom report builder
- Git commit with reporting and analytics

#### Validation Tests
1. Test report generation
2. Verify analytics calculations
3. Check export formats
4. Test scheduled reports

---

## 9. Device Data Visualization

### Description
Create interfaces for visualizing parsed device data with filtering, sorting, and tabbed navigation.

### 9.1. Device Listing View

#### Description
Create a device listing view with filtering and sorting capabilities.

#### AI Prompt
```
I need to create a device listing view with advanced filtering and sorting. Please:

1. Implement device list view:
   - Responsive table with key device information
   - Status indicators with icons
   - Advanced filtering by multiple properties
   - Column sorting and customization
2. Add search capabilities:
   - Full-text search
   - Search by IP, hostname, serial, etc.
   - Type-ahead suggestions
   - Recent search history
3. Implement quick actions:
   - Context menu for common actions
   - Bulk operations
   - Export selected devices
   - Device comparison
4. Create view customization:
   - Column selection
   - Saved views
   - Display density options

Please include git commit instructions.
```

#### Implementation Steps
1. Create device list view
2. Implement filtering and sorting
3. Add search capabilities
4. Create quick actions
5. Implement view customization

#### Deliverables
- Device list view
- Filtering and sorting
- Search functionality
- Quick actions
- View customization
- Git commit with device listing view

#### Validation Tests
1. Test filtering and sorting
2. Verify search functionality
3. Check quick actions
4. Test view customization

### 9.2. Device Detail View Framework

#### Description
Create the framework for device detail view with tabbed navigation.

#### AI Prompt
```
I need to create a framework for device detail view with tabbed navigation. Please:

1. Implement device detail layout:
   - Header with key device information
   - Tabbed navigation system
   - Content area for tab content
   - Sidebar for actions and metadata
2. Create tab infrastructure:
   - Dynamic tab loading
   - URL hash navigation
   - Tab state persistence
   - Permission-based tab visibility
3. Add common components:
   - Status indicators
   - Last updated information
   - Version selector
   - Action buttons
4. Implement breadcrumb navigation

Please include git commit instructions.
```

#### Implementation Steps
1. Create device detail layout
2. Implement tabbed navigation
3. Add common components
4. Create breadcrumb navigation
5. Implement permission checks

#### Deliverables
- Device detail layout
- Tabbed navigation system
- Common components
- Breadcrumb navigation
- Git commit with device detail framework

#### Validation Tests
1. Test tab navigation
2. Verify URL hash functionality
3. Check permission-based visibility
4. Test breadcrumb navigation

### 9.3. Interface Data Visualization

#### Description
Create the interfaces tab with visualization of interface data.

#### AI Prompt
```
I need to create the interfaces tab with comprehensive interface data visualization. Please:

1. Implement interface listing:
   - Sortable and filterable table
   - Status indicators
   - Capacity utilization
   - IP addressing information
2. Add detailed views:
   - Interface details modal/page
   - Configuration display
   - Historical metrics
   - Connected devices
3. Create visualizations:
   - Interface status summary charts
   - VLAN distribution
   - IP subnet visualization
   - Interface type breakdown
4. Implement export functionality

Please include git commit instructions.
```

#### Implementation Steps
1. Create interface listing component
2. Implement detailed views
3. Add visualizations
4. Create export functionality
5. Add filtering and search

#### Deliverables
- Interface listing component
- Detailed interface views
- Visualizations
- Export functionality
- Git commit with interface visualization

#### Validation Tests
1. Test interface listing with filtering
2. Verify detailed views display correctly
3. Check visualizations with sample data
4. Test export functionality

### 9.4. Routing Data Visualization

#### Description
Create the routing tab with visualization of routing data.

#### AI Prompt
```
I need to create the routing tab with routing table visualization. Please:

1. Implement routing table view:
   - Protocol-based grouping
   - Filterable and sortable entries
   - Next-hop visualization
   - Administrative distance and metrics
2. Add routing protocol sections:
   - OSPF, EIGRP, BGP specific data
   - Neighbor information
   - Area/AS visualizations
   - Route redistribution
3. Create network visualizations:
   - Subnet hierarchy visualization
   - Route path visualization
   - Next-hop relationship diagram
   - Connected networks map
4. Implement search and filtering

Please include git commit instructions.
```

#### Implementation Steps
1. Create routing table view
2. Implement protocol-specific sections
3. Add network visualizations
4. Create search and filtering
5. Add export functionality

#### Deliverables
- Routing table view
- Protocol-specific sections
- Network visualizations
- Search and filtering
- Git commit with routing visualization

#### Validation Tests
1. Test routing table display
2. Verify protocol-specific data
3. Check network visualizations
4. Test search and filtering

### 9.5. ACL and Security Visualization

#### Description
Create the access lists tab with visualization of security data.

#### AI Prompt
```
I need to create the access lists tab with ACL details visualization. Please:

1. Implement ACL listing:
   - Grouped by interface/purpose
   - Rule display with explanation
   - Hit count information (if available)
   - Referenced objects
2. Add rule details:
   - Source/destination visualization
   - Service and protocol information
   - Action and logging display
   - Time-based conditions
3. Create security visualizations:
   - Traffic flow diagrams
   - Allow/deny distribution
   - Object usage heatmap
   - Rule overlap detection
4. Implement search and filtering

Please include git commit instructions.
```

#### Implementation Steps
1. Create ACL listing component
2. Implement rule details view
3. Add security visualizations
4. Create search and filtering
5. Add export functionality

#### Deliverables
- ACL listing component
- Rule details view
- Security visualizations
- Search and filtering
- Git commit with ACL visualization

#### Validation Tests
1. Test ACL display with sample data
2. Verify rule details view
3. Check security visualizations
4. Test search and filtering

### 9.6. Neighbor and Topology Visualization

#### Description
Create the neighbors tab with CDP/LLDP information visualization.

#### AI Prompt
```
I need to create the neighbors tab with CDP/LLDP information visualization. Please:

1. Implement neighbor listing:
   - Device discovery protocol data
   - Connection details
   - Platform information
   - Capability flags
2. Add topology visualization:
   - Interactive network graph
   - Connection details on hover/select
   - Zoom and pan controls
   - Filtering options
3. Create detailed neighbor views:
   - Connection information
   - Protocol-specific details
   - Historical data
   - Quick actions
4. Implement export functionality

Please include git commit instructions.
```

#### Implementation Steps
1. Create neighbor listing component
2. Implement topology visualization
3. Add detailed neighbor views
4. Create export functionality
5. Add filtering options

#### Deliverables
- Neighbor listing component
- Topology visualization
- Detailed neighbor views
- Export functionality
- Git commit with neighbor visualization

#### Validation Tests
1. Test neighbor listing with sample data
2. Verify topology visualization
3. Check detailed neighbor views
4. Test export functionality

### 9.7. Advanced Filtering and Search

#### Description
Implement advanced filtering and search capabilities for device data.

#### AI Prompt
```
I need to implement advanced filtering and search capabilities for device data. Please:

1. Create unified search system:
   - Cross-tab search functionality
   - Deep search in configuration
   - Regular expression support
   - Search history and favorites
2. Implement advanced filtering:
   - Multiple criteria selection
   - Dynamic filter builder
   - Saved filter sets
   - Quick filter presets
3. Add visualization filtering:
   - Chart-based filtering
   - Click-to-filter in visualizations
   - Visual filter state indicators
   - Filter chaining
4. Create filter sharing functionality

Please include git commit instructions.
```

#### Implementation Steps
1. Create unified search system
2. Implement advanced filtering
3. Add visualization filtering
4. Create filter sharing
5. Add search history and favorites

#### Deliverables
- Unified search system
- Advanced filtering
- Visualization filtering
- Filter sharing
- Git commit with advanced filtering and search

#### Validation Tests
1. Test search with various queries
2. Verify advanced filtering
3. Check visualization filtering
4. Test filter sharing

### 9.8. Data Export Integration

#### Description
Integrate export functionality into device data visualization.

#### AI Prompt
```
I need to integrate export functionality into device data visualization. Please:

1. Implement export options:
   - Current view export
   - Selected items export
   - Complete dataset export
   - Format selection (CSV, Excel, PDF)
2. Create export customization:
   - Column selection
   - Format options
   - File naming
   - Metadata inclusion
3. Add background processing:
   - Progress indication
   - Email notification on completion
   - Download link generation
   - Export history
4. Implement scheduled exports

Please include git commit instructions.
```

#### Implementation Steps
1. Implement export options
2. Create export customization
3. Add background processing
4. Implement scheduled exports
5. Create export history

#### Deliverables
- Export options
- Export customization
- Background processing
- Scheduled exports
- Git commit with data export integration

#### Validation Tests
1. Test different export formats
2. Verify customization options
3. Check background processing
4. Test scheduled exports

### 9.9. Tab Management System

#### Description
Implement a system for creating, managing, and customizing tabs for different device data views.

#### AI Prompt
```
I need to implement a tab management system for device data visualization. This system should allow administrators to create default tab configurations and users to create custom tab views. Please:

1. Create a tab management model:
   - Tab name and description
   - Visibility controls (show/hide)
   - Vendor and OS associations
   - Ownership (admin/user)
   - Category assignment
   - Order/priority
2. Implement tab builder interface:
   - Drag-and-drop data field selection
   - Available vs. implemented fields
   - Field reordering within tabs
   - Tab preview capability
3. Add tab configuration system:
   - Default admin-managed tabs
   - User-specific custom tabs
   - Cloning from existing tabs
   - Import/export of tab configurations
4. Create tab permission system:
   - Global tabs (all users)
   - Customer-specific tabs
   - User-specific tabs
   - Sharing capabilities

Please include git commit instructions.
```

#### Implementation Steps
1. Create tab management models
2. Implement tab builder interface
3. Add tab configuration system
4. Create tab permission system
5. Implement tab import/export

#### Deliverables
- Tab management models
- Tab builder interface
- Configuration system
- Permission system
- Git commit with tab management system

#### Validation Tests
1. Test creating and editing tabs
2. Verify field selection and ordering
3. Check permission-based visibility
4. Test import/export functionality

### 9.10. Data Field Management System

#### Description
Implement a system for managing data fields to be displayed in tabs.

#### AI Prompt
```
I need to implement a data field management system that allows administrators and users to select which data fields appear in tabs. Please:

1. Create field management models:
   - Field name and description
   - Data type and format
   - Source mapping (JSON path in parsed data)
   - Default formatting
   - Grouping/category
2. Implement field selector interface:
   - Available fields repository
   - Selected fields for implementation
   - Search and filtering
   - Drag-and-drop reordering
3. Add field normalization system:
   - Cross-vendor field mapping
   - OS-specific field handling
   - Default value handling
   - Format standardization
4. Create field dependency tracking:
   - Related field identification
   - Dependency visualization
   - Automatic inclusion of dependencies
   - Impact analysis for changes

Please include git commit instructions.
```

#### Implementation Steps
1. Create field management models
2. Implement field selector interface
3. Add field normalization system
4. Create field dependency tracking
5. Implement field metadata management

#### Deliverables
- Field management models
- Field selector interface
- Normalization system
- Dependency tracking
- Git commit with field management system

#### Validation Tests
1. Test field selection across vendors
2. Verify field normalization
3. Check dependency tracking
4. Test reordering and organization

### 9.11. Multi-Vendor Data Normalization

#### Description
Implement a system to normalize data from different vendors and OS versions for consistent display.

#### AI Prompt
```
I need to implement a multi-vendor data normalization system that enables consistent display of network data regardless of source device type. Please:

1. Create data mapping framework:
   - Vendor-specific field mappings
   - OS version variations
   - Common data model definitions
   - Transformation rules
2. Implement normalization engine:
   - Field name standardization
   - Value format normalization
   - Unit conversion
   - Enum/status standardization
3. Add configuration interface:
   - Mapping rule management
   - Test and validation tools
   - Bulk import/export
   - Version control for mappings
4. Create validation and testing system:
   - Sample data validation
   - Regression testing
   - Coverage reporting
   - Error handling and logging

Please include git commit instructions.
```

#### Implementation Steps
1. Create data mapping framework
2. Implement normalization engine
3. Add configuration interface
4. Create validation system
5. Document mapping strategies

#### Deliverables
- Data mapping framework
- Normalization engine
- Configuration interface
- Validation system
- Git commit with data normalization system

#### Validation Tests
1. Test normalization across vendors
2. Verify consistent data display
3. Check handling of OS variations
4. Test with actual device data

### 9.12. Template Management System

#### Description
Implement a system for managing templates that define how data is displayed in tabs.

#### AI Prompt
```
I need to implement a template management system for defining how data is displayed in tabs. The system should support different device types, vendors, and OS versions. Please:

1. Create template models:
   - Template name and description
   - Vendor and OS associations
   - Category and purpose
   - Default field selections
   - Layout configurations
2. Implement template builder:
   - Visual template designer
   - Field placement and organization
   - Conditional display rules
   - Styling options
3. Add template testing tools:
   - Preview with sample data
   - Multi-vendor testing
   - Validation tools
   - Performance testing
4. Create template library:
   - Default templates
   - Community-shared templates
   - Version control
   - Import/export capabilities

Please include git commit instructions.
```

#### Implementation Steps
1. Create template models
2. Implement template builder
3. Add template testing tools
4. Create template library
5. Implement versioning system

#### Deliverables
- Template models
- Template builder interface
- Testing tools
- Template library
- Git commit with template management system

#### Validation Tests
1. Test template creation and editing
2. Verify multi-vendor support
3. Check preview and testing tools
4. Test template sharing and versioning

### 9.13. AI-Assisted Template Generation

#### Description
Implement AI-assisted template generation for different device types.

#### AI Prompt
```
I need to implement AI-assisted template generation for device configuration display. The system should suggest templates based on device type, vendor, and available data. Please:

1. Create AI suggestion system:
   - Device type analysis
   - Data field categorization
   - Template pattern recognition
   - Relevance scoring
2. Implement template generator:
   - Default template creation
   - Field grouping suggestions
   - Layout optimization
   - Tab organization
3. Add learning capabilities:
   - User feedback collection
   - Template popularity tracking
   - Continuous improvement
   - Pattern recognition
4. Create suggestion interface:
   - Template recommendations
   - Interactive refinement
   - Preview and testing
   - One-click application

Please include git commit instructions.
```

#### Implementation Steps
1. Create AI suggestion system
2. Implement template generator
3. Add learning capabilities
4. Create suggestion interface
5. Implement feedback system

#### Deliverables
- AI suggestion system
- Template generator
- Learning capabilities
- Suggestion interface
- Git commit with AI-assisted template generation

#### Validation Tests
1. Test template suggestions
2. Verify quality of generated templates
3. Check learning from feedback
4. Test with various device types

### 9.14. Integrated Testing System

#### Description
Implement a comprehensive testing system for tab and template configurations.

#### AI Prompt
```
I need to implement an integrated testing system for tab and template configurations. The system should ensure that configurations work correctly across different vendors and data formats. Please:

1. Create test framework:
   - Test case management
   - Sample data repositories
   - Expected result definitions
   - Automated verification
2. Implement test execution:
   - Template testing
   - Tab configuration testing
   - Cross-vendor validation
   - Regression testing
3. Add test reporting:
   - Test coverage analysis
   - Success/failure metrics
   - Visual comparison
   - Error categorization
4. Create continuous testing:
   - Integration with CI/CD
   - Scheduled validation runs
   - Change impact analysis
   - Notification system

Please include git commit instructions.
```

#### Implementation Steps
1. Create test framework
2. Implement test execution
3. Add test reporting
4. Create continuous testing
5. Build sample data repository

#### Deliverables
- Test framework
- Test execution system
- Reporting dashboard
- Continuous testing integration
- Git commit with integrated testing system

#### Validation Tests
1. Test framework with multiple templates
2. Verify cross-vendor validation
3. Check reporting accuracy
4. Test notification system

---

## 10. Data Comparison System

### Description
Implement functionality to compare device configurations across different iterations or between devices.

### 10.1. Comparison Selection Interface

#### Description
Create an interface for selecting devices and iterations to compare.

#### AI Prompt
```
I need to create an interface for selecting devices and iterations to compare. Please:

1. Implement selection interface:
   - Device selector with search
   - Iteration/version selector
   - Side-by-side preview
   - Comparison type options
2. Add comparison modes:
   - Same device, different iterations
   - Different devices, same time
   - Custom selection
   - Baseline comparison
3. Create selection workflow:
   - Guided selection process
   - Quick selection shortcuts
   - Recent comparison history
   - Saved comparison configurations
4. Implement validation and suggestions

Please include git commit instructions.
```

#### Implementation Steps
1. Create selection interface
2. Implement comparison modes
3. Add selection workflow
4. Create validation and suggestions
5. Add comparison history

#### Deliverables
- Selection interface
- Comparison modes
- Selection workflow
- Validation and suggestions
- Git commit with comparison selection interface

#### Validation Tests
1. Test device and iteration selection
2. Verify comparison modes
3. Check selection workflow
4. Test validation and suggestions

### 10.2. Side-by-Side Comparison View

#### Description
Implement side-by-side comparison view for device data.

#### AI Prompt
```
I need to implement a side-by-side comparison view for device data. Please:

1. Create comparison layout:
   - Two or more panes for data display
   - Synchronized scrolling
   - Expandable sections
   - Summary header
2. Implement data display:
   - Structured data comparison
   - Configuration text comparison
   - Raw data comparison option
   - Metadata and context display
3. Add navigation features:
   - Jump to next difference
   - Section navigation
   - Collapsible sections
   - Search within comparison
4. Create responsive design for different screens

Please include git commit instructions.
```

#### Implementation Steps
1. Create comparison layout
2. Implement data display
3. Add navigation features
4. Create responsive design
5. Add synchronized scrolling

#### Deliverables
- Comparison layout
- Data display components
- Navigation features
- Responsive design
- Git commit with side-by-side comparison view

#### Validation Tests
1. Test comparison layout with sample data
2. Verify synchronized scrolling
3. Check navigation features
4. Test responsive design

### 10.3. Difference Highlighting

#### Description
Implement highlighting of differences in compared data.

#### AI Prompt
```
I need to implement highlighting of differences in compared data. Please:

1. Create difference detection:
   - Field-level comparison
   - Text-based diff algorithm
   - Structural comparison
   - Semantic understanding
2. Implement visual highlighting:
   - Added/removed/changed indicators
   - Color coding for difference types
   - Expandable contextual information
   - Diff summary
3. Add difference categorization:
   - Critical vs. minor differences
   - Configuration vs. state changes
   - Expected vs. unexpected changes
   - Impactful changes highlighting
4. Create interactive features for differences

Please include git commit instructions.
```

#### Implementation Steps
1. Create difference detection algorithms
2. Implement visual highlighting
3. Add difference categorization
4. Create interactive features
5. Add summary statistics

#### Deliverables
- Difference detection algorithms
- Visual highlighting components
- Difference categorization
- Interactive features
- Git commit with difference highlighting

#### Validation Tests
1. Test difference detection with various data
2. Verify visual highlighting
3. Check difference categorization
4. Test interactive features

### 10.4. Tabbed Comparison Interface

#### Description
Create tabbed interface for comparing different data types.

#### AI Prompt
```
I need to create a tabbed interface for comparing different data types in our device comparison view. Please:

1. Implement tab structure:
   - Overview/summary tab
   - Interfaces comparison tab
   - Routing comparison tab
   - ACL comparison tab
   - Additional data type tabs
2. Create synchronized tab navigation:
   - Consistent tab selection across panes
   - URL hash navigation
   - Tab state persistence
   - Tab-specific controls
3. Add difference summary:
   - Per-tab difference counts
   - Visual indicators
   - Quick navigation to tabs with differences
   - Difference severity indicators
4. Implement tab-specific comparison views

Please include git commit instructions.
```

#### Implementation Steps
1. Create tab structure
2. Implement synchronized tab navigation
3. Add difference summary
4. Create tab-specific comparison views
5. Add URL hash navigation

#### Deliverables
- Tab structure
- Synchronized tab navigation
- Difference summary
- Tab-specific comparison views
- Git commit with tabbed comparison interface

#### Validation Tests
1. Test tab navigation
2. Verify synchronized tab selection
3. Check difference summary
4. Test tab-specific views

### 10.5. Filtering in Comparison

#### Description
Implement filtering options for comparison views.

#### AI Prompt
```
I need to implement filtering options for comparison views. Please:

1. Create filter controls:
   - Show only differences
   - Filter by change type (added, removed, modified)
   - Filter by component type
   - Filter by importance/impact
2. Implement filter application:
   - Real-time filtering
   - URL parameters for filter state
   - Filter state persistence
   - Clear filters option
3. Add advanced filtering:
   - Filter by specific fields
   - Text-based filtering
   - Regular expression support
   - Custom filter rules
4. Create filter presets and sharing

Please include git commit instructions.
```

#### Implementation Steps
1. Create filter controls
2. Implement filter application
3. Add advanced filtering
4. Create filter presets
5. Add filter state persistence

#### Deliverables
- Filter controls
- Filter application logic
- Advanced filtering
- Filter presets
- Git commit with comparison filtering

#### Validation Tests
1. Test basic filtering
2. Verify advanced filtering
3. Check filter state persistence
4. Test filter presets

### 10.6. Comparison Export

#### Description
Implement export functionality for comparison results.

#### AI Prompt
```
I need to implement export functionality for comparison results. Please:

1. Create export options:
   - PDF report with highlighting
   - Excel spreadsheet with differences
   - HTML report
   - JSON/YAML data format
2. Implement customization:
   - Include/exclude sections
   - Difference highlighting options
   - Metadata inclusion
   - Annotation options
3. Add background processing:
   - Progress tracking
   - Email notification
   - Download link generation
   - Export history
4. Create report templates for comparison

Please include git commit instructions.
```

#### Implementation Steps
1. Create export options
2. Implement customization
3. Add background processing
4. Create report templates
5. Add export history

#### Deliverables
- Export options
- Customization interface
- Background processing
- Report templates
- Git commit with comparison export

#### Validation Tests
1. Test different export formats
2. Verify customization options
3. Check background processing
4. Test report templates

---

## 11. Export System

### Description
Implement functionality to export device data in various formats (XLSX, CSV, PDF).

### 11.1. Export Service Layer

#### Description
Create an export service layer to handle various export types.

#### AI Prompt
```
I need to create an export service layer for handling various export types. Please:

1. Design service architecture:
   - Pluggable format handlers
   - Common interface
   - Background processing support
   - Error handling and recovery
2. Implement core export service:
   - Configuration and options handling
   - Data retrieval and preparation
   - Task management
   - Result storage
3. Add export tracking:
   - Export history model
   - Status tracking
   - Result storage
   - Cleanup policies
4. Create management commands for maintenance

Please include git commit instructions.
```

#### Implementation Steps
1. Design service architecture
2. Implement core export service
3. Add export tracking
4. Create background task integration
5. Add management commands

#### Deliverables
- Export service architecture
- Core export service
- Export tracking
- Background task integration
- Git commit with export service layer

#### Validation Tests
1. Test core export functionality
2. Verify format handler pluggability
3. Check background processing
4. Test export tracking

### 11.2. Format-Specific Exporters

#### Description
Implement format-specific exporters for different file types.

#### AI Prompt
```
I need to implement format-specific exporters for different file types. Please:

1. Create Excel (XLSX) exporter:
   - Workbook and worksheet generation
   - Styling and formatting
   - Formula support
   - Multi-sheet exports
2. Implement CSV exporter:
   - Configurable delimiters
   - Encoding options
   - Escaping and quoting
   - Header options
3. Add PDF exporter:
   - Report templates
   - Page layout and styling
   - Image and chart inclusion
   - Table formatting
4. Create JSON/YAML exporters:
   - Structure customization
   - Pretty printing options
   - Schema inclusion
   - Metadata options

Please include git commit instructions.
```

#### Implementation Steps
1. Create Excel (XLSX) exporter
2. Implement CSV exporter
3. Add PDF exporter
4. Create JSON/YAML exporters
5. Add common base class

#### Deliverables
- Excel exporter
- CSV exporter
- PDF exporter
- JSON/YAML exporters
- Git commit with format-specific exporters

#### Validation Tests
1. Test Excel export with formatting
2. Verify CSV export options
3. Check PDF report generation
4. Test JSON/YAML structure

### 11.3. Export Option Interface

#### Description
Create user interface for export options and configuration.

#### AI Prompt
```
I need to create a user interface for export options and configuration. Please:

1. Implement export dialog:
   - Format selection
   - Option configuration
   - Preview capability
   - Progress indication
2. Create option controls:
   - Content selection (columns, sections)
   - Formatting options
   - File naming
   - Delivery method
3. Add advanced options:
   - Filtering before export
   - Transformation options
   - Scheduling options
   - Recurring exports
4. Implement responsive design

Please include git commit instructions.
```

#### Implementation Steps
1. Create export dialog component
2. Implement option controls
3. Add advanced options
4. Create responsive design
5. Add preview capability

#### Deliverables
- Export dialog component
- Option controls
- Advanced options
- Responsive design
- Git commit with export option interface

#### Validation Tests
1. Test export dialog with various options
2. Verify option controls work correctly
3. Check advanced options
4. Test on different screen sizes

### 11.4. Background Processing for Exports

#### Description
Implement background processing for large exports.

#### AI Prompt
```
I need to implement background processing for large exports. Please:

1. Create background task integration:
   - Celery task definition
   - Progress tracking
   - Result handling
   - Error recovery
2. Implement progress UI:
   - Real-time progress updates
   - Cancellation option
   - Estimated completion time
   - Status messaging
3. Add result handling:
   - Download link generation
   - Email notification
   - In-app notification
   - Temporary storage management
4. Create export management interface

Please include git commit instructions.
```

#### Implementation Steps
1. Create background task integration
2. Implement progress UI
3. Add result handling
4. Create export management interface
5. Add error recovery

#### Deliverables
- Background task integration
- Progress UI
- Result handling
- Export management interface
- Git commit with background processing

#### Validation Tests
1. Test large export processing
2. Verify progress updates
3. Check result handling
4. Test error recovery

### 11.5. Email Notification System

#### Description
Implement email notifications for export completion.

#### AI Prompt
```
I need to implement an email notification system for export completion. Please:

1. Create notification service:
   - Email template system
   - Queue management
   - Retry mechanism
   - Delivery tracking
2. Implement email templates:
   - Export completion template
   - Download link inclusion
   - Expiration information
   - Customizable messages
3. Add notification preferences:
   - User preference settings
   - Notification types
   - Delivery timing options
   - Digest options
4. Create notification history

Please include git commit instructions.
```

#### Implementation Steps
1. Create notification service
2. Implement email templates
3. Add notification preferences
4. Create notification history
5. Add retry mechanism

#### Deliverables
- Notification service
- Email templates
- Notification preferences
- Notification history
- Git commit with email notification system

#### Validation Tests
1. Test email sending for exports
2. Verify template rendering
3. Check notification preferences
4. Test retry mechanism

### 11.6. Custom Export Templates

#### Description
Implement customizable export templates.

#### AI Prompt
```
I need to implement customizable export templates. Please:

1. Create template system:
   - Template model with version control
   - Template editor UI
   - Template testing functionality
   - Sharing options
2. Implement template components:
   - Reusable content blocks
   - Dynamic data binding
   - Conditional logic
   - Styling options
3. Add template management:
   - Template library
   - Import/export templates
   - Template categories
   - Default templates
4. Create template documentation

Please include git commit instructions.
```

#### Implementation Steps
1. Create template system
2. Implement template components
3. Add template management
4. Create template documentation
5. Add template sharing

#### Deliverables
- Template system
- Template components
- Template management
- Template documentation
- Git commit with custom export templates

#### Validation Tests
1. Test template creation and editing
2. Verify template rendering
3. Check template sharing
4. Test template import/export

### 11.7. Export System Testing

#### Description
Create comprehensive tests for the export system.

#### AI Prompt
```
I need to create comprehensive tests for our export system. Please:

1. Implement unit tests:
   - Format handler tests
   - Option validation
   - Service layer tests
   - Template rendering
2. Create integration tests:
   - End-to-end export flow
   - Background processing
   - Email notification
   - Template system
3. Add performance tests:
   - Large dataset handling
   - Memory usage
   - Processing time
   - Concurrency testing
4. Create test fixtures and utilities

Please include git commit instructions.
```

#### Implementation Steps
1. Create unit tests for components
2. Implement integration tests
3. Add performance tests
4. Create test fixtures
5. Document testing approach

#### Deliverables
- Unit test suite
- Integration tests
- Performance tests
- Test fixtures
- Git commit with export system tests

#### Validation Tests
1. Run test suite and verify coverage
2. Check performance metrics
3. Verify handling of edge cases
4. Test concurrency scenarios

---

## 12. SSH Connectivity

### Description
Implement direct SSH connectivity to network devices for data collection.

### 12.1. Netmiko Integration

#### Description
Integrate Netmiko for SSH connections to network devices.

#### AI Prompt
```
I need to integrate Netmiko for SSH connections to network devices. Please:

1. Add Netmiko dependency:
   - Install and configure
   - Version management
   - Compatibility testing
   - Documentation
2. Create connection utilities:
   - Device type mapping
   - Connection parameter handling
   - Session management
   - Error handling
3. Implement basic operations:
   - Command execution
   - Config mode operations
   - File transfer
   - Terminal settings
4. Add connection pooling and reuse

Please include git commit instructions.
```

#### Implementation Steps
1. Add Netmiko as a dependency
2. Create connection utilities
3. Implement basic operations
4. Add connection pooling
5. Create error handling

#### Deliverables
- Netmiko dependency added
- Connection utilities
- Basic operations implementation
- Connection pooling
- Git commit with Netmiko integration

#### Validation Tests
1. Test connection to sample devices (or mocks)
2. Verify command execution
3. Check error handling
4. Test connection pooling

### 12.2. Credential Management

#### Description
Implement secure credential storage and management.

#### AI Prompt
```
I need to implement secure credential storage and management for network devices. Please:

1. Create credential model:
   - Username and password fields with encryption
   - Key-based authentication support
   - Device/group association
   - Privilege level settings
2. Implement secure storage:
   - Encryption at rest
   - Secure retrieval
   - Masking in logs and UI
   - Audit logging
3. Add credential management UI:
   - CRUD operations
   - Testing capability
   - Bulk operations
   - Import/export
4. Create credential rotation system

Please include git commit instructions.
```

#### Implementation Steps
1. Create credential model with encryption
2. Implement secure storage
3. Add credential management UI
4. Create credential rotation system
5. Add audit logging

#### Deliverables
- Credential model
- Secure storage implementation
- Management UI
- Credential rotation system
- Git commit with credential management

#### Validation Tests
1. Test credential encryption
2. Verify secure retrieval
3. Check audit logging
4. Test credential rotation

### 12.3. Command Template System

#### Description
Create a command template system for different device types.

#### AI Prompt
```
I need to create a command template system for different device types. Please:

1. Design template structure:
   - YAML/JSON format
   - Device type mapping
   - Argument substitution
   - Conditional logic
2. Implement template engine:
   - Parser for template syntax
   - Context-based rendering
   - Error handling
   - Default fallbacks
3. Create template library:
   - Common commands
   - Vendor-specific commands
   - Show commands
   - Configuration commands
4. Add management interface

Please include git commit instructions.
```

#### Implementation Steps
1. Design template structure
2. Implement template engine
3. Create template library
4. Add management interface
5. Document template system

#### Deliverables
- Template structure design
- Template engine
- Template library
- Management interface
- Git commit with command template system

#### Validation Tests
1. Test template rendering
2. Verify argument substitution
3. Check device type mapping
4. Test conditional logic

### 12.4. Connection Management

#### Description
Implement connection management for SSH sessions.

#### AI Prompt
```
I need to implement connection management for SSH sessions. Please:

1. Create connection manager:
   - Session tracking
   - Timeout handling
   - Retry logic
   - Concurrent connection limiting
2. Implement connection pooling:
   - Session reuse
   - Pool configuration
   - Health checking
   - Cleanup
3. Add monitoring and statistics:
   - Connection metrics
   - Performance tracking
   - Error reporting
   - Usage statistics
4. Create management commands

Please include git commit instructions.
```

#### Implementation Steps
1. Create connection manager
2. Implement connection pooling
3. Add monitoring and statistics
4. Create management commands
5. Add error recovery logic

#### Deliverables
- Connection manager
- Connection pooling
- Monitoring and statistics
- Management commands
- Git commit with connection management

#### Validation Tests
1. Test connection management
2. Verify timeout and retry handling
3. Check monitoring and statistics
4. Test concurrent connections

### 12.5. SSH Command Execution

#### Description
Implement secure command execution and parsing for SSH sessions.

#### AI Prompt
```
I need to implement secure command execution and parsing for SSH sessions. Please:

1. Create command execution service:
   - Single command execution
   - Script/multi-command execution
   - Interactive command support
   - Timeout and interrupt handling
2. Implement result parsing:
   - Output structure detection
   - Error pattern detection
   - Prompt recognition
   - Table and data extraction
3. Add security features:
   - Command authorization
   - Prohibited command checking
   - Result sanitization
   - Rate limiting
4. Create logging and auditing

Please include git commit instructions.
```

#### Implementation Steps
1. Create command execution service
2. Implement result parsing
3. Add security features
4. Create logging and auditing
5. Add timeout and interrupt handling

#### Deliverables
- Command execution service
- Result parsing
- Security features
- Logging and auditing
- Git commit with SSH command execution

#### Validation Tests
1. Test command execution
2. Verify result parsing
3. Check security features
4. Test logging and auditing

### 12.6. Scheduled Collection

#### Description
Implement scheduled collection capabilities for SSH connectivity.

#### AI Prompt
```
I need to implement scheduled collection capabilities for SSH connectivity. Please:

1. Create scheduling system:
   - Schedule definition model
   - Frequency and timing options
   - One-time vs recurring
   - Device/group targeting
2. Implement task generation:
   - Command template selection
   - Parameter substitution
   - Task queuing
   - Priority management
3. Add results handling:
   - Parsing and storage
   - Notification on completion
   - Error handling
   - Iteration tracking
4. Create scheduling UI

Please include git commit instructions.
```

#### Implementation Steps
1. Create scheduling system
2. Implement task generation
3. Add results handling
4. Create scheduling UI
5. Add error notification

#### Deliverables
- Scheduling system
- Task generation
- Results handling
- Scheduling UI
- Git commit with scheduled collection

#### Validation Tests
1. Test schedule creation
2. Verify task generation
3. Check results handling
4. Test error notification

---

## 13. API Integration

### Description
Implement API integration for cloud-managed network platforms like Meraki.

### 13.1. API Client Architecture

#### Description
Create a base API client architecture for platform integrations.

#### AI Prompt
```
I need to create a base API client architecture for network platform integrations. Please:

1. Design client architecture:
   - Abstract base client
   - Platform-specific implementations
   - Authentication handling
   - Request/response processing
2. Implement core functionality:
   - HTTP request handling
   - Response parsing
   - Error handling
   - Rate limiting
3. Add common utilities:
   - Pagination handling
   - Parameter serialization
   - Response transformation
   - Caching
4. Create client registration system

Please include git commit instructions.
```

#### Implementation Steps
1. Design client architecture
2. Implement core functionality
3. Add common utilities
4. Create client registration system
5. Document extension points

#### Deliverables
- Client architecture design
- Core functionality
- Common utilities
- Client registration system
- Git commit with API client architecture

#### Validation Tests
1. Test core HTTP functionality
2. Verify error handling
3. Check rate limiting
4. Test client registration

### 13.2. Platform-Specific Clients

#### Description
Implement platform-specific API clients for network management platforms.

#### AI Prompt
```
I need to implement platform-specific API clients for network management platforms. Please:

1. Create Cisco Meraki client:
   - Authentication and endpoints
   - Organization/network/device methods
   - Configuration/monitoring capabilities
   - Data transformation
2. Implement Arista CloudVision client:
   - Token-based authentication
   - Device management
   - Configuration methods
   - Telemetry collection
3. Add additional clients as needed:
   - Cisco DNA Center
   - Juniper Mist
## Implementation Sequence

To efficiently implement the Network Configuration Parser application, follow this recommended sequence:

1. **Project Setup**: Initialize the base project structure
2. **Core Models**: Define the data foundation
3. **Parser Integration**: Set up the core parsing functionality
4. **Data Modeling**: Create standardized data models
5. **Authentication System**: Implement user management
6. **File Upload System**: Enable configuration uploads
7. **Basic Dashboard**: Create the primary interface
8. **Customer & Project Management**: Add organizational capabilities
9. **Device Data Visualization**: Display parsed data
10. **Data Comparison System**: Allow configuration comparisons
11. **Export System**: Enable data exports
12. **SSH Connectivity**: Add direct device connection
13. **API Integration**: Connect to cloud platforms
14. **Testing & Quality Assurance**: Ensure reliability
15. **Containerization**: Package for deployment

Each component should be completed and validated before moving to the next, ensuring a solid foundation for subsequent features. 