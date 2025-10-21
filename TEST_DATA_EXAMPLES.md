# Visa Application Intake - Test Data Examples

## Example 1: Complete Application (from your requirements)

### Application Details
```
Visa Application Number: [Auto-generated UUID or custom]
Case Type: Schengen Short Stay
Visa Type Requested: Short Stay
Application Type: MVV
Submission Date: 05/04/2023
Intake Location: Sydney FO
Applicant is minor?: No
Urgent: Yes
```

### Applicant Information
```
Given Name(s): Ellie
Surname / Family Name(s): Pearce
Surname at Birth: Walsh
Variation in Birth Certificate?: No
Gender / Sex: Female
Current Nationality: Australian
Country of Nationality: Australia
```

### Address
```
Street: Eugella Road
House Number: 11
Unit Number / Lot#: A
Postal Code: 4802
City: Mount Rooper
Country: Australia
```

### Birth Information
```
Date of Birth: Year only (incomplete)
Date of Birth Indicator: Incomplete: Only year
Year of Birth: YYYY
State of Birth: NSW
Place of Birth: Snowy Plain
Country of Birth: Australia
Nationality at Birth: Australian
```

### Additional Information
```
Residency Status in Australia: Permanent Resident
Civil Status: Married
Privileged Member of EU?: No
Occupation: Unemployed
```

---

## Example 2: Alternative Test Case

### Application Details
```
Visa Application Number: [Auto-generated]
Case Type: Long Stay
Visa Type Requested: Business
Application Type: Initial
Submission Date: 15/06/2023
Intake Location: Melbourne FO
Applicant is minor?: No
Urgent: No
```

### Applicant Information
```
Given Name(s): James
Surname / Family Name(s): Thompson
Surname at Birth: Thompson
Variation in Birth Certificate?: No
Gender / Sex: Male
Current Nationality: British
Country of Nationality: United Kingdom
```

### Address
```
Street: Collins Street
House Number: 250
Unit Number / Lot#: 3B
Postal Code: 3000
City: Melbourne
Country: Australia
```

### Birth Information
```
Date of Birth Indicator: Complete: Day, month and year
Date of Birth: 15/03/1985
State of Birth: England
Place of Birth: London
Country of Birth: United Kingdom
Nationality at Birth: British
```

### Additional Information
```
Residency Status in Australia: Temporary Resident
Civil Status: Single
Privileged Member of EU?: Yes
Occupation: Employed
```

---

## Example 3: Minor Application

### Application Details
```
Visa Application Number: [Auto-generated]
Case Type: Schengen Short Stay
Visa Type Requested: Tourist
Application Type: Initial
Submission Date: 20/08/2023
Intake Location: Brisbane FO
Applicant is minor?: Yes
Urgent: No
```

### Applicant Information
```
Given Name(s): Sophie
Surname / Family Name(s): Chen
Surname at Birth: Chen
Variation in Birth Certificate?: No
Gender / Sex: Female
Current Nationality: Australian
Country of Nationality: Australia
```

### Address
```
Street: Queen Street
House Number: 88
Unit Number / Lot#: [blank]
Postal Code: 4000
City: Brisbane
Country: Australia
```

### Birth Information
```
Date of Birth Indicator: Complete: Day, month and year
Date of Birth: 10/12/2015
State of Birth: QLD
Place of Birth: Brisbane
Country of Birth: Australia
Nationality at Birth: Australian
```

### Additional Information
```
Residency Status in Australia: Citizen
Civil Status: Single
Privileged Member of EU?: No
Occupation: Student
```

---

## API Usage Examples

### Creating Example 1 via API:

```python
from services.visa_application_service import VisaApplicationService

visa_service = VisaApplicationService(azure_handler)

application_data = {
    'case_type': 'Schengen Short Stay',
    'visa_type_requested': 'Short Stay',
    'application_type': 'MVV',
    'submission_date': '05/04/2023',
    'intake_location': 'Sydney FO',
    'applicant_is_minor': False,
    'is_urgent': True,
    'given_name': 'Ellie',
    'surname': 'Pearce',
    'surname_at_birth': 'Walsh',
    'variation_in_birth_certificate': False,
    'gender': 'Female',
    'country_of_nationality': 'Australia',
    'street_number': 'Eugella Road 11',
    'unit_number': 'A',
    'postal_code': '4802',
    'city': 'Mount Rooper',
    'country': 'Australia',
    'date_of_birth': 'YYYY',
    'date_of_birth_indicator': 'Incomplete: Only year',
    'state_of_birth': 'NSW',
    'place_of_birth': 'Snowy Plain',
    'country_of_birth': 'Australia',
    'nationality_at_birth': 'Australian',
    'residency_status_in_australia': 'Permanent Resident',
    'civil_status': 'Married',
    'packaged_member_of_eu': False,
    'occupation': 'Unemployed',
    'created_by': 'test_user',
    'status': 'Submitted'
}

app_number = visa_service.create_application(application_data)
print(f"Application created: {app_number}")
```

### Querying Applications:

```python
# Get all urgent applications
urgent_apps = visa_service.list_applications("IsUrgent eq true")

# Get all applications from Sydney
sydney_apps = visa_service.list_applications("IntakeLocation eq 'Sydney FO'")

# Get all draft applications
draft_apps = visa_service.list_applications("Status eq 'Draft'")

# Get all minor applications
minor_apps = visa_service.list_applications("ApplicantIsMinor eq true")

# Combine filters (urgent AND Sydney)
urgent_sydney = visa_service.list_applications(
    "IsUrgent eq true and IntakeLocation eq 'Sydney FO'"
)
```

### Updating an Application:

```python
# Change status from Draft to Submitted
visa_service.update_application(app_number, {
    'status': 'Submitted'
})

# Update occupation
visa_service.update_application(app_number, {
    'occupation': 'Employed'
})

# Update multiple fields
visa_service.update_application(app_number, {
    'status': 'Approved',
    'occupation': 'Self-Employed',
    'is_urgent': False
})
```

---

## Field Options Reference

### Case Types
- Schengen Short Stay
- Long Stay
- Transit
- Other

### Application Types
- Initial
- MVV
- Renewal
- Extension

### Visa Types Requested
- Short Stay
- Long Stay
- Transit
- Business
- Tourist
- Family Visit
- Other

### Intake Locations
- Sydney FO
- Melbourne FO
- Brisbane FO
- Perth FO
- Adelaide FO

### Gender Options
- Female
- Male
- Other
- Prefer not to say

### Countries (Common)
- Australia
- New Zealand
- United Kingdom
- United States
- Canada
- Other

### Date of Birth Indicators
- Complete: Day, month and year
- Incomplete: Only year
- Incomplete: Month and year

### Residency Status in Australia
- Citizen
- Permanent Resident
- Temporary Resident
- Visitor
- Other

### Civil Status
- Single
- Married
- De Facto
- Divorced
- Widowed
- Separated

### Occupation
- Employed
- Unemployed
- Self-Employed
- Student
- Retired
- Other

### Yes/No Fields
- Applicant is Minor?
- Urgent
- Variation in Birth Certificate?
- Privileged Member of EU?

---

## Status Values

### Current Statuses
- **Draft**: Application saved but not submitted
- **Submitted**: Application completed and submitted

### Future Statuses (for enhancement)
- Under Review
- Additional Information Required
- Approved
- Rejected
- Withdrawn
- Cancelled
- Processing
- Interview Scheduled
- Awaiting Documents

---

## Testing Checklist

When testing the intake form, verify:

- [ ] All required fields enforce validation
- [ ] Optional fields can be left blank
- [ ] Date picker works correctly
- [ ] Dropdowns show all options
- [ ] "Save as Draft" creates application with Status='Draft'
- [ ] "Save Application" creates application with Status='Submitted'
- [ ] Application number is generated and displayed
- [ ] Success message appears after saving
- [ ] Form can be cleared with "Clear Form" button
- [ ] Session authentication is enforced
- [ ] User activity is tracked
- [ ] Created applications appear in Azure Table Storage
- [ ] CreatedBy field captures logged-in username
- [ ] Timestamps are recorded correctly

---

## Common OData Filters

```python
# Single field equals
"Status eq 'Draft'"
"CaseType eq 'Schengen Short Stay'"
"IsUrgent eq true"

# Multiple conditions (AND)
"IsUrgent eq true and IntakeLocation eq 'Sydney FO'"

# Multiple conditions (OR)
"CaseType eq 'Long Stay' or CaseType eq 'Transit'"

# Not equals
"Status ne 'Draft'"

# Greater than (for dates if stored as datetime)
"CreatedAt gt datetime'2023-01-01T00:00:00Z'"

# Contains (for string fields)
"substringof('Sydney', IntakeLocation)"

# Starts with
"startswith(Surname, 'Pe')"
```

---

## Quick Start Commands

### Setup:
```powershell
# Create the table
python src/util/setup_visa_table.py

# Run tests
python src/util/test_visa_service.py

# Start application
streamlit run src/main.py
```

### Access:
```
URL: http://localhost:8501
Page: Visa Intake (in sidebar)
Authentication: Required
```

---

## Support

For questions or issues:
- Review: `VISA_INTAKE_README.md`
- Architecture: `ARCHITECTURE.md`
- Implementation: `IMPLEMENTATION_SUMMARY.md`
- Email: support@visacheck.com
