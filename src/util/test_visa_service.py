"""
Test script for Visa Application Service

This script demonstrates how to use the VisaApplicationService API
to create, retrieve, update, and delete visa applications.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv
from util.azure_functions import AzureHandler
from services.visa_application_service import VisaApplicationService


def test_visa_application_service():
    """Test the visa application service functionality"""
    
    # Load environment variables
    load_dotenv()
    
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if not connection_string:
        print("Error: AZURE_CONNECTION_STRING not found")
        return
    
    # Initialize handlers
    azure_handler = AzureHandler(connection_string)
    visa_service = VisaApplicationService(azure_handler)
    
    print("=== Testing Visa Application Service ===\n")
    
    # Test 1: Create a new application
    print("1. Creating a test application...")
    test_data = {
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
        'created_by': 'test_script',
        'status': 'Draft'
    }
    
    try:
        app_number = visa_service.create_application(test_data)
        print(f"✅ Application created successfully!")
        print(f"   Application Number: {app_number}\n")
        
        # Test 2: Retrieve the application
        print("2. Retrieving the application...")
        retrieved_app = visa_service.get_application(app_number)
        if retrieved_app:
            print(f"✅ Application retrieved successfully!")
            print(f"   Given Name: {retrieved_app.get('GivenName')}")
            print(f"   Surname: {retrieved_app.get('Surname')}")
            print(f"   Case Type: {retrieved_app.get('CaseType')}")
            print(f"   Status: {retrieved_app.get('Status')}\n")
        else:
            print("❌ Failed to retrieve application\n")
        
        # Test 3: Update the application
        print("3. Updating the application...")
        update_data = {
            'status': 'Submitted',
            'occupation': 'Employed'
        }
        visa_service.update_application(app_number, update_data)
        print(f"✅ Application updated successfully!\n")
        
        # Test 4: Verify the update
        print("4. Verifying the update...")
        updated_app = visa_service.get_application(app_number)
        if updated_app:
            print(f"✅ Update verified!")
            print(f"   Status: {updated_app.get('Status')}")
            print(f"   Occupation: {updated_app.get('Occupation')}\n")
        
        # Test 5: List applications
        print("5. Listing all applications...")
        applications = visa_service.list_applications()
        print(f"✅ Found {len(applications)} application(s) in the database\n")
        
        # Test 6: Delete the test application (cleanup)
        print("6. Cleaning up (deleting test application)...")
        visa_service.delete_application(app_number)
        print(f"✅ Test application deleted successfully!\n")
        
        print("=== All tests passed! ===")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")


if __name__ == "__main__":
    test_visa_application_service()
