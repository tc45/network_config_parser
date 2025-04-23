# System Architecture and Component Interaction Diagrams

This document contains Mermaid diagrams that illustrate the architecture and interactions between different components of the Network Configuration Parser application.

## System Architecture Overview

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[Web UI]
        API[API Endpoints]
    end
    
    subgraph "Business Logic Layer"
        AuthService[Authentication Service]
        ParserService[Parser Service]
        ExportService[Export Service]
        SSHService[SSH Service]
        APIClientService[API Client Service]
        ComparisonService[Comparison Service]
    end
    
    subgraph "Data Layer"
        Django[Django ORM]
        DB[(Database)]
        Storage[File Storage]
    end
    
    subgraph "External Systems"
        NetworkDevices[Network Devices]
        CloudAPIs[Cloud APIs]
    end
    
    UI --> AuthService
    UI --> ParserService
    UI --> ExportService
    UI --> SSHService
    UI --> APIClientService
    UI --> ComparisonService
    
    API --> AuthService
    API --> ParserService
    API --> ExportService
    API --> SSHService
    API --> APIClientService
    API --> ComparisonService
    
    AuthService --> Django
    ParserService --> Django
    ExportService --> Django
    SSHService --> Django
    APIClientService --> Django
    ComparisonService --> Django
    
    Django --> DB
    ParserService --> Storage
    ExportService --> Storage
    
    SSHService --> NetworkDevices
    APIClientService --> CloudAPIs
```

## Data Flow: Device Configuration Processing

```mermaid
sequenceDiagram
    participant User as User
    participant WebUI as Web UI
    participant ParserSvc as Parser Service
    participant NTC as NTC Templates
    participant PydanticModel as Pydantic Models
    participant Storage as Database
    
    User ->> WebUI: Upload Show Tech Output
    WebUI ->> ParserSvc: Process Show Tech File
    ParserSvc ->> ParserSvc: Identify Device Type
    ParserSvc ->> ParserSvc: Extract Command Outputs
    
    loop For Each Command
        ParserSvc ->> NTC: Parse Command Output
        NTC -->> ParserSvc: Structured Data
        ParserSvc ->> PydanticModel: Validate & Transform
        PydanticModel -->> ParserSvc: Validated Models
    end
    
    ParserSvc ->> Storage: Store Parsed Data
    Storage -->> ParserSvc: Confirmation
    ParserSvc -->> WebUI: Processing Complete
    WebUI -->> User: Show Success & Results Link
```

## User Management and Authentication

```mermaid
graph TD
    subgraph "Authentication"
        Login[Login]
        Register[Register]
        Logout[Logout]
        PasswordReset[Password Reset]
    end
    
    subgraph "Authorization"
        Permissions[Permissions]
        Roles[Roles]
        AccessControl[Access Control]
    end
    
    subgraph "User Management"
        UserProfile[User Profile]
        UserPreferences[User Preferences]
        UserActivity[User Activity]
    end
    
    subgraph "Resources"
        Customers[Customers]
        Projects[Projects]
        Devices[Devices]
        ParsedData[Parsed Data]
    end
    
    User[User] --> Login
    User --> Register
    User --> Logout
    User --> PasswordReset
    
    Login --> Permissions
    Register --> Permissions
    
    Permissions --> Roles
    Roles --> AccessControl
    
    AccessControl --> Customers
    AccessControl --> Projects
    AccessControl --> Devices
    AccessControl --> ParsedData
    
    User --> UserProfile
    User --> UserPreferences
    UserProfile --> UserActivity
```

## Parser Component Interaction

```mermaid
graph TB
    subgraph "Input Sources"
        FileUpload[File Upload]
        SSHCollection[SSH Collection]
        APICollection[API Collection]
    end
    
    subgraph "Parser System"
        DeviceTypeIdentifier[Device Type Identifier]
        CommandExtractor[Command Extractor]
        
        subgraph "Device Parsers"
            CiscoIOSParser[Cisco IOS Parser]
            CiscoNXOSParser[Cisco NXOS Parser]
            CiscoASAParser[Cisco ASA Parser]
            PaloAltoParser[Palo Alto Parser]
            OtherVendorParsers[Other Vendor Parsers]
        end
        
        NTCTemplates[NTC Templates]
        PydanticModels[Pydantic Models]
    end
    
    subgraph "Output Processors"
        DataStorage[Data Storage]
        DataTransformers[Data Transformers]
        ExportFormatters[Export Formatters]
    end
    
    FileUpload --> DeviceTypeIdentifier
    SSHCollection --> DeviceTypeIdentifier
    APICollection --> DeviceTypeIdentifier
    
    DeviceTypeIdentifier --> CommandExtractor
    CommandExtractor --> CiscoIOSParser
    CommandExtractor --> CiscoNXOSParser
    CommandExtractor --> CiscoASAParser
    CommandExtractor --> PaloAltoParser
    CommandExtractor --> OtherVendorParsers
    
    CiscoIOSParser --> NTCTemplates
    CiscoNXOSParser --> NTCTemplates
    CiscoASAParser --> NTCTemplates
    PaloAltoParser --> NTCTemplates
    OtherVendorParsers --> NTCTemplates
    
    NTCTemplates --> PydanticModels
    PydanticModels --> DataStorage
    PydanticModels --> DataTransformers
    DataTransformers --> ExportFormatters
```

## Data Model Overview

```mermaid
erDiagram
    USER ||--o{ CUSTOMER : manages
    USER }|--o{ USER_CUSTOMER : has_access
    USER_CUSTOMER }|--|| CUSTOMER : refers_to
    
    CUSTOMER ||--o{ PROJECT : owns
    PROJECT ||--o{ DEVICE : contains
    DEVICE ||--o{ DEVICE_ITERATION : has_versions
    
    DEVICE_ITERATION ||--o{ INTERFACE_DATA : contains
    DEVICE_ITERATION ||--o{ ROUTING_DATA : contains
    DEVICE_ITERATION ||--o{ ACL_DATA : contains
    DEVICE_ITERATION ||--o{ NAT_DATA : contains
    DEVICE_ITERATION ||--o{ NEIGHBORS_DATA : contains
    DEVICE_ITERATION ||--o{ MISC_DATA : contains
    
    USER {
        int id PK
        string username
        string email
        string password_hash
        datetime last_login
        boolean is_active
        boolean is_staff
        boolean is_superuser
    }
    
    CUSTOMER {
        int id PK
        string name
        string description
        datetime created_at
        datetime updated_at
    }
    
    USER_CUSTOMER {
        int id PK
        int user_id FK
        int customer_id FK
        string role
        datetime created_at
    }
    
    PROJECT {
        int id PK
        int customer_id FK
        string name
        string description
        datetime created_at
        datetime updated_at
    }
    
    DEVICE {
        int id PK
        int project_id FK
        string hostname
        string vendor
        string platform
        string model
        string serial_number
        string mgmt_ip
        datetime discovered_at
        datetime updated_at
    }
    
    DEVICE_ITERATION {
        int id PK
        int device_id FK
        string name
        datetime captured_at
        string source_file
        string source_type
        datetime processed_at
    }
    
    INTERFACE_DATA {
        int id PK
        int device_iteration_id FK
        string name
        string description
        string status
        string ip_address
        string subnet_mask
        string vlan
        string mtu
        string speed
        string duplex
    }
    
    ROUTING_DATA {
        int id PK
        int device_iteration_id FK
        string protocol
        string destination
        string mask
        string next_hop
        string interface
        int metric
        int distance
    }
    
    ACL_DATA {
        int id PK
        int device_iteration_id FK
        string acl_name
        string line_num
        string action
        string protocol
        string source
        string destination
        string service
        string remarks
    }
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Client"
        Browser[Web Browser]
    end
    
    subgraph "Docker Environment"
        subgraph "Django Application"
            Nginx[Nginx]
            Gunicorn[Gunicorn]
            Django[Django App]
            Celery[Celery Workers]
        end
        
        subgraph "Data Services"
            PostgreSQL[(PostgreSQL)]
            Redis[(Redis)]
        end
    end
    
    subgraph "Network Devices"
        Routers[Routers]
        Switches[Switches]
        Firewalls[Firewalls]
    end
    
    Browser --> Nginx
    Nginx --> Gunicorn
    Gunicorn --> Django
    Django --> PostgreSQL
    Django --> Redis
    Django --> Celery
    Celery --> PostgreSQL
    Celery --> Redis
    Celery --> Routers
    Celery --> Switches
    Celery --> Firewalls
``` 