"""Login page for st.navigation"""
import time
import streamlit as st
import re

from util.auth_functions import AuthHandler, check_password
from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.session_manager import SessionManager

def validate_email(email):
    """Simple email validation."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email)

def login_page():
    """Login page function"""
    # Get handlers from session state
    auth_handler = st.session_state.get('auth_handler')
    azure_handler = st.session_state.get('azure_handler')
    table_name = st.session_state.get('table_name_users')
    
    if not auth_handler or not azure_handler or not table_name:
        st.error("Application initialization error. Please refresh the page.")
        return

    # Handle user login for shared or personal password
    def handle_successful_login():
        SessionManager.initialize_session(
            user=username,
            user_engagement=retrieved_user.engagement,
            is_admin=retrieved_user.isAdmin
        )
        # Navigation will be handled automatically by st.navigation
        st.rerun()

    # Display login page and handle login logic.
    st.title("Login")

    username = st.text_input("Email").lower()
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_handler = UserHandler(azure_handler, table_name)        
        retrieved_user = user_handler.get_user(username=username)

        # Step 2: If user exists (manually created), skip email validation
        if retrieved_user is not None:
            stored_password_hash = retrieved_user.password_hash

            # Check if the user has a personal password
            if stored_password_hash:
                # Validate personal password with bcrypt
                if check_password(password, retrieved_user):
                    # Successful login, update last login timestamp
                    user_handler.update_user(username)
                    if retrieved_user.last_time_of_use != None and auth_handler.check_password_expiration(retrieved_user):
                        st.session_state['password_expired'] = True

                    handle_successful_login()
                else:
                    st.error("Incorrect personal password.")
            else:
                st.session_state['password_expired'] = True
                handle_successful_login()

        else:   
            # Step 3: Validate email format for shared password users (if user does not exist)             
            if not validate_email(username):
                st.error("Please enter a valid email address.")
                return
            
            st.error("Incorrect password.")