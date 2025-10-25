"""Setup script to initialize the Visa Applications table in Azure Table Storage"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent.parent
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv
from util.azure_functions import AzureHandler

def setup_visa_applications_table():
    """Create the VisaApplications table if it doesn't exist"""
    # Load environment variables
    load_dotenv()
    
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if not connection_string:
        print("Error: AZURE_CONNECTION_STRING not found in environment variables")
        return False
    
    try:
        # Initialize Azure handler
        azure_handler = AzureHandler(connection_string)
        
        # Table name
        table_name = "VisaApplications"
        
        # Check if table exists
        if azure_handler.check_table_exists(table_name):
            print(f"✅ Table '{table_name}' already exists")
            return True
        
        # Create the table
        print(f"Creating table '{table_name}'...")
        azure_handler.create_tables([table_name])
        print(f"✅ Table '{table_name}' created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up table: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Visa Applications Table Setup ===")
    setup_visa_applications_table()
