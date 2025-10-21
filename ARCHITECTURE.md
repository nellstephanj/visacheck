# Visa Application Intake - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          Streamlit Navigation (src/main.py)              │ │
│  │  ┌─────────┬──────────┬────────┬──────────┬────────────┐ │ │
│  │  │  Login  │ VisaCheck│  Visa  │  Admin   │  Password  │ │ │
│  │  │   🔐    │    📄    │ Intake │   🛠️    │    🔏     │ │ │
│  │  │         │          │   📋   │          │            │ │ │
│  │  └─────────┴──────────┴────┬───┴──────────┴────────────┘ │ │
│  └────────────────────────────┼──────────────────────────────┘ │
└─────────────────────────────────┼────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VISA INTAKE PAGE                             │
│                  (src/pages/intake.py)                          │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │  Form Sections:     │  │  Actions:           │             │
│  │  • Application #    │  │  • Save Application │             │
│  │  • Application Info │  │  • Save as Draft    │             │
│  │  • Applicant        │  │  • Clear Form       │             │
│  │  • Address          │  └─────────────────────┘             │
│  │  • Birth Info       │                                       │
│  │  • Additional Info  │                                       │
│  └─────────────────────┘                                       │
│                                                                 │
│         │                                                       │
│         │ Form Submission                                      │
│         ▼                                                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            Session Management                           │  │
│  │  • Authentication Check                                 │  │
│  │  • Activity Tracking                                    │  │
│  │  • Validation                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ API Call
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                │
│          (src/services/visa_application_service.py)             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  VisaApplicationService                                   │ │
│  │                                                           │ │
│  │  Methods:                                                 │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ • create_application(data) → app_number            │ │ │
│  │  │   - Generates UUID                                  │ │ │
│  │  │   - Validates data                                  │ │ │
│  │  │   - Adds timestamps                                 │ │ │
│  │  │   - Returns application number                      │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ • get_application(app_number) → dict               │ │ │
│  │  │   - Retrieves by application number                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ • update_application(app_number, data) → void      │ │ │
│  │  │   - Merges updates                                  │ │ │
│  │  │   - Updates timestamp                               │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ • delete_application(app_number) → void            │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ • list_applications(filter) → list                 │ │ │
│  │  │   - Supports OData filtering                        │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Azure SDK Call
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                            │
│              (src/util/azure_functions.py)                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  AzureHandler                                             │ │
│  │  • insert_entity()                                        │ │
│  │  • retrieve_entity()                                      │ │
│  │  • update_entity()                                        │ │
│  │  • delete_entity()                                        │ │
│  │  • retrieve_table_items()                                 │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AZURE TABLE STORAGE                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Table: VisaApplications                                  │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │ PartitionKey: 'VisaApplication'                     │ │ │
│  │  │ RowKey: UUID (Application Number)                   │ │ │
│  │  │                                                     │ │ │
│  │  │ Fields:                                             │ │ │
│  │  │ • ApplicationNumber                                 │ │ │
│  │  │ • CaseType                                          │ │ │
│  │  │ • VisaTypeRequested                                 │ │ │
│  │  │ • ApplicationType                                   │ │ │
│  │  │ • SubmissionDate                                    │ │ │
│  │  │ • IntakeLocation                                    │ │ │
│  │  │ • GivenName, Surname                                │ │ │
│  │  │ • Gender, CountryOfNationality                      │ │ │
│  │  │ • Address fields                                    │ │ │
│  │  │ • Birth information                                 │ │ │
│  │  │ • ResidencyStatusInAustralia                        │ │ │
│  │  │ • CivilStatus, Occupation                           │ │ │
│  │  │ • CreatedAt, UpdatedAt, CreatedBy                   │ │ │
│  │  │ • Status (Draft/Submitted)                          │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Creating a New Application

```
User fills form
      ↓
Click "Save Application"
      ↓
Form validation (required fields)
      ↓
Build application_data dict
      ↓
visa_service.create_application(application_data)
      ↓
Generate UUID for application number
      ↓
Add timestamps (CreatedAt, UpdatedAt)
      ↓
Add audit info (CreatedBy, Status)
      ↓
azure_handler.insert_entity(table_name, entity)
      ↓
Azure SDK call to Table Storage
      ↓
Entity stored in VisaApplications table
      ↓
Return application_number to user
      ↓
Display success message with app_number
```

### Retrieving an Application

```
Call visa_service.get_application(app_number)
      ↓
azure_handler.retrieve_entity(table, partition_key, row_key)
      ↓
Azure SDK query by RowKey
      ↓
Return entity dict
      ↓
Access fields: entity['GivenName'], entity['Status'], etc.
```

### Updating an Application

```
Call visa_service.update_application(app_number, update_data)
      ↓
Retrieve existing entity
      ↓
Merge update_data into existing entity
      ↓
Update 'UpdatedAt' timestamp
      ↓
azure_handler.update_entity(table_name, entity)
      ↓
Azure SDK MERGE operation
      ↓
Entity updated in Table Storage
```

## File Organization

```
visacheck/
├── src/
│   ├── main.py                              # Entry point, navigation setup
│   ├── pages/
│   │   ├── intake.py                        # 📋 Intake form UI (NEW)
│   │   ├── homepage.py                      # Main page
│   │   ├── login.py                         # Login page
│   │   ├── admin.py                         # Admin page
│   │   └── password.py                      # Password change
│   ├── services/
│   │   ├── __init__.py                      # (NEW)
│   │   └── visa_application_service.py      # 🔧 API layer (NEW)
│   ├── util/
│   │   ├── azure_functions.py               # Azure Table Storage handler
│   │   ├── session_manager.py               # Session management
│   │   ├── setup_visa_table.py              # 🔧 DB setup (NEW)
│   │   └── test_visa_service.py             # 🧪 Tests (NEW)
│   └── config/
│       └── settings.py                      # Configuration
├── VISA_INTAKE_README.md                     # 📚 User guide (NEW)
├── IMPLEMENTATION_SUMMARY.md                 # 📝 Implementation doc (NEW)
└── ARCHITECTURE.md                           # 🏗️ This file (NEW)
```

## Security Architecture

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │ HTTPS
       ▼
┌──────────────────────────────────────┐
│  Streamlit Application               │
│  ┌────────────────────────────────┐  │
│  │  Session Management            │  │
│  │  • is_valid()                  │  │
│  │  • check_timeout()             │  │
│  │  • update_activity()           │  │
│  └────────────────────────────────┘  │
│              ▼                       │
│  ┌────────────────────────────────┐  │
│  │  Authentication Required       │  │
│  │  • User must be logged in      │  │
│  │  • Session must be active      │  │
│  └────────────────────────────────┘  │
│              ▼                       │
│  ┌────────────────────────────────┐  │
│  │  Audit Trail                   │  │
│  │  • CreatedBy: username         │  │
│  │  • CreatedAt: timestamp        │  │
│  │  • UpdatedAt: timestamp        │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
                ▼
┌──────────────────────────────────────┐
│  Azure Table Storage                 │
│  • Encrypted at rest                 │
│  • Encrypted in transit              │
│  • Access key required               │
└──────────────────────────────────────┘
```

## Key Design Decisions

### 1. **Service Layer Pattern**
- Separates business logic from UI
- Enables code reuse
- Makes testing easier
- Allows API changes without UI changes

### 2. **Azure Table Storage**
- NoSQL for flexible schema
- Cost-effective
- High availability
- Integrates with existing infrastructure

### 3. **UUID for Application Numbers**
- Guaranteed uniqueness
- No collisions
- Distributed generation
- Can be changed to custom format if needed

### 4. **Status Field**
- Draft: Work in progress
- Submitted: Complete application
- Extensible for future statuses (Approved, Rejected, etc.)

### 5. **Flexible Date of Birth**
- Handles incomplete dates
- Indicator field shows data completeness
- Future-proof for various scenarios

### 6. **Audit Trail**
- CreatedBy: User accountability
- Timestamps: Change tracking
- Essential for compliance

## Extension Points

### Easy to Add:
1. **Application List View**: Use `list_applications()` API
2. **Search Functionality**: Use OData filters
3. **Status Workflow**: Add more status values
4. **Email Notifications**: Hook into create/update methods
5. **Document Attachments**: Add file upload to form
6. **PDF Export**: Add rendering service
7. **Bulk Operations**: Use existing APIs in loops
8. **Reporting**: Query table with filters

## Performance Considerations

### Caching
- `AzureHandler` caches table clients
- Session state reuses service instances

### Scalability
- Azure Table Storage handles millions of entities
- Partitioning by 'VisaApplication' allows efficient queries
- Can add secondary partition keys if needed

### Optimization Opportunities
- Add indexes for common queries
- Implement pagination for list views
- Cache frequently accessed applications
- Add batch operations for bulk updates

## Monitoring & Logging

```python
import logging
logger = logging.getLogger(__name__)

# Service layer logs:
logger.info(f"Created visa application: {application_number}")
logger.warning(f"Entity not found: {application_number}")
logger.error(f"Error creating visa application: {str(e)}")
```

All operations are logged for:
- Debugging
- Audit trail
- Performance monitoring
- Error tracking
