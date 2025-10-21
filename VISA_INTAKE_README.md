# Visa Application Intake Module

## Overview
This module adds a comprehensive intake form for visa applications to the VisaCheck system. It captures all necessary applicant information in a structured format and stores it in Azure Table Storage.

## Features

### 1. Intake Form (`src/pages/intake.py`)
A multi-section form that captures:

#### Application Number
- Unique identifier for the visa application

#### Application Details
- **Case Type**: Schengen Short Stay, Long Stay, Transit, Other
- **Application Type**: Initial, MVV, Renewal, Extension
- **Visa Type Requested**: Short Stay, Long Stay, Transit, Business, Tourist, Family Visit, Other
- **Submission Date**: Date the application was submitted
- **Intake Location**: Sydney FO, Melbourne FO, Brisbane FO, Perth FO, Adelaide FO
- **Applicant is Minor**: Yes/No
- **Urgent**: Yes/No flag

#### Applicant Information
- **Given Name(s)**: Applicant's first name(s)
- **Surname**: Family name
- **Surname at Birth**: Birth surname if different
- **Variation in Birth Certificate**: Yes/No
- **Gender/Sex**: Female, Male, Other, Prefer not to say
- **Current Nationality**: Dropdown selection
- **Country of Nationality**: Text input

#### Address Details
- **Street**: Street name
- **House Number**: House number
- **Unit Number/Lot#/Suffix**: Unit identifier
- **Postal Code**: Postal/ZIP code
- **City**: City name
- **Country**: Country of residence

#### Birth Information
- **Date of Birth Indicator**: Complete, Year only, Month and year
- **Date of Birth**: Full date, year only, or month/year based on indicator
- **Place of Birth**: City/town of birth
- **State of Birth**: State/province of birth
- **Country of Birth**: Country of birth
- **Nationality at Birth**: Original nationality

#### Additional Information
- **Residency Status in Australia**: Citizen, Permanent Resident, Temporary Resident, Visitor, Other
- **Civil Status**: Single, Married, De Facto, Divorced, Widowed, Separated
- **Privileged Member of EU**: Yes/No
- **Occupation**: Employed, Unemployed, Self-Employed, Student, Retired, Other

### 2. Data Service Layer (`src/services/visa_application_service.py`)
A comprehensive service class that handles all database operations:

#### Methods:
- `create_application(application_data)`: Creates a new visa application
- `get_application(application_number)`: Retrieves an application by number
- `update_application(application_number, application_data)`: Updates an existing application
- `delete_application(application_number)`: Deletes an application
- `list_applications(filter_query)`: Lists applications with optional filtering

#### Data Structure:
All applications are stored in Azure Table Storage with:
- **PartitionKey**: 'VisaApplication'
- **RowKey**: Application Number (UUID)
- All form fields as entity properties
- Timestamps: CreatedAt, UpdatedAt
- Audit fields: CreatedBy, Status

### 3. Database Setup (`src/util/setup_visa_table.py`)
A utility script to initialize the Azure Table Storage table for visa applications.

## Installation & Setup

### 1. Install Dependencies
No additional dependencies needed - uses existing Azure Table Storage connection.

### 2. Initialize Database Table
Run the setup script to create the VisaApplications table:

```powershell
python src/util/setup_visa_table.py
```

### 3. Configure Environment Variables
Ensure your `.env` file contains:
```
AZURE_CONNECTION_STRING=your_connection_string_here
```

## Usage

### Accessing the Intake Form
1. Log in to the VisaCheck application
2. Navigate to "Visa Intake" from the sidebar
3. Fill in the required information
4. Choose to either:
   - **Save Application**: Submit the complete application
   - **Save as Draft**: Save progress without submitting
   - **Clear Form**: Reset all fields

### Form Validation
- Required fields are marked with an asterisk (*)
- The form validates all required fields before submission
- Missing fields are highlighted with error messages

### Data Persistence
- All applications are stored in Azure Table Storage
- Each application receives a unique application number
- Applications can be retrieved, updated, or deleted via the service layer
- Audit trail includes creation/update timestamps and user information

## API Integration

### Creating an Application
```python
from services.visa_application_service import VisaApplicationService

visa_service = VisaApplicationService(azure_handler)

application_data = {
    'case_type': 'Schengen Short Stay',
    'visa_type_requested': 'Short Stay',
    'application_type': 'Initial',
    'submission_date': '05/09/2023',
    'intake_location': 'Sydney FO',
    'given_name': 'Test',
    'surname': 'Person',
    # ... more fields
}

app_number = visa_service.create_application(application_data)
```

### Retrieving an Application
```python
application = visa_service.get_application(app_number)
```

### Updating an Application
```python
update_data = {
    'status': 'Approved',
    'occupation': 'Employed'
}
visa_service.update_application(app_number, update_data)
```

### Listing Applications
```python
# All applications
all_apps = visa_service.list_applications()

# Filtered applications (OData filter)
urgent_apps = visa_service.list_applications("IsUrgent eq true")
```

## Navigation Integration
The intake page is automatically added to the navigation menu for authenticated users. It appears as "Visa Intake" with a 📋 icon.

## Security
- Session authentication required
- Activity tracking integrated
- User information logged with each application
- Session timeout protection

## Future Enhancements
Potential improvements:
1. Application search and listing page
2. Edit existing applications
3. Document upload integration
4. Status tracking workflow
5. Email notifications
6. Bulk import/export functionality
7. Advanced filtering and reporting
8. Application approval workflow

## File Structure
```
src/
├── pages/
│   └── intake.py                          # Intake form UI
├── services/
│   ├── __init__.py
│   └── visa_application_service.py        # Data service layer
└── util/
    └── setup_visa_table.py                # Table initialization script
```

## Testing
To test the intake form:
1. Run the application: `streamlit run src/main.py`
2. Log in with valid credentials
3. Navigate to "Visa Intake"
4. Fill in test data
5. Submit the form
6. Check Azure Table Storage for the created entry

## Troubleshooting

### Table Not Found Error
Run the setup script:
```powershell
python src/util/setup_visa_table.py
```

### Connection String Error
Verify the `AZURE_CONNECTION_STRING` in your `.env` file.

### Form Submission Fails
Check:
- All required fields are filled
- Azure Table Storage is accessible
- Network connectivity

## Support
For issues or questions:
- Email: support@visacheck.com
- Bug reports: support@visacheck.com
