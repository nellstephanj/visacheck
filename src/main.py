import streamlit as st
import os

from dotenv import load_dotenv

st.set_page_config(
    page_title="VisaCheck",
    page_icon=os.path.join(os.path.dirname(__file__), "Favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

from util.session_manager import SessionManager
from util.session_cleanup import SessionCleanup
from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.auth_functions import AuthHandler

from app_pages.init_page import init_form



def main_page(azure_handler: AzureHandler, table_name: str):
    # All session state initialization is now handled by SessionManager.initialize_session()

    user_handler = UserHandler(azure_handler, table_name)  

    # Enhanced session validation and recovery
    if not SessionManager.is_valid():
        # Try to recover session state
        if not SessionManager.recover_session_state(user_handler):
            st.query_params["page"] = "login"
            st.rerun()
    
    # Check for session timeout with warning
    session_valid, warning_msg = SessionManager.check_timeout()
    if not session_valid:
        st.query_params["page"] = "login"
        st.rerun()
    elif warning_msg:
        st.warning(warning_msg)
    
    # Update activity on page access
    SessionManager.update_activity()

    st.title('VisaCheck')
    st.write("Application initialized successfully.")


def main():
    # Load environment variables from .env file
    load_dotenv()
    table_name_users = os.getenv("TABLE_NAME_USERS")

    # Initialize the AzureHandler
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if connection_string is None:
        st.error("Unable to retrieve connection string")
        return
    if table_name_users is None:
        st.error("Unable to retrieve users table name")
        return

    # Create Azure handler (internal caching handles performance)
    azure_handler = AzureHandler(connection_string)
    user_handler = UserHandler(azure_handler, table_name_users)

    # Initialize singleton background cleanup scheduler
    SessionCleanup.ensure_scheduler_running()

    # Check if an initial admin user has been created, if not prompt user to create user
    if not azure_handler.check_table_exists(table_name_users):
        init_form(user_handler, azure_handler)  
        return

    # Initialize session state if not already done
    if 'processed_files' not in st.session_state:
        st.session_state['processed_files'] = []

    if "password_expired" not in st.session_state:
        st.session_state["password_expired"] = False

    auth_handler = AuthHandler(azure_handler)

    # Store handlers in session state for page access
    st.session_state['azure_handler'] = azure_handler
    st.session_state['user_handler'] = user_handler  
    st.session_state['auth_handler'] = auth_handler
    st.session_state['table_name_users'] = table_name_users

    # NEW: Dynamic navigation based on authentication
    pages = []
    
    # Check authentication state
    is_authenticated = st.session_state.get('user') is not None
    is_admin = st.session_state.get('is_admin', False)
    password_expired = st.session_state.get('password_expired', False)
    
    # Import page wrapper functions
    from pages.login import login_page
    from pages.homepage import main_page_wrapper
    from pages.admin import admin_page
    from pages.password import password_page
    from pages.intake import intake_page
    from pages.matching import matching_page
    from pages.active_applications import active_applications_page
    from pages.workflow import workflow_page
    from pages.case_assignment import case_assignment_page
    
    if not is_authenticated:
        # Not authenticated - only login page
        pages = [st.Page(login_page, title="Login", icon="🔐")]
    elif password_expired:
        # Password expired - force password change
        pages = [st.Page(password_page, title="Change Password", icon="🔏")]
    else:
        # Authenticated - main pages
        pages = [
            st.Page(main_page_wrapper, title="VisaCheck", icon="📄"),
            st.Page(active_applications_page, title="Active Applications", icon="📊"),
            st.Page(case_assignment_page, title="Case Assignment", icon="🎯"),
            st.Page(workflow_page, title="Sexy Visa Agent", icon="🤖"),
            st.Page(intake_page, title="Visa Intake", icon="📋"),
            st.Page(matching_page, title="EU-VIS Matching", icon="🔍")
        ]
        
        # Add admin page if user is admin
        if is_admin:
            pages.append(st.Page(admin_page, title="Admin", icon="🛠️"))
        
        # Always add password change for authenticated users
        pages.append(st.Page(password_page, title="Change Password", icon="🔏"))
    
    # Create and run navigation
    nav = st.navigation(pages, position="sidebar")
    nav.run()
        
if __name__ == "__main__":
    main()

# # To run, use this line in terminal: streamlit run c:\Users\fdevrien\Projects\tryout_project\main_streamlit.py