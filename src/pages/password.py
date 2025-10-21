"""Password update page for st.navigation"""
import streamlit as st
import os

from util.user_functions import UserHandler
from util.azure_functions import AzureHandler
from util.auth_functions import check_password_complexity, hash_password, check_password
from util.sidebar import sidebar

def password_page():
    """Password update page function"""
    # Add sidebar
    sidebar()
    
    # Get handlers from session state
    azure_handler = st.session_state.get('azure_handler')
    table_name = st.session_state.get('table_name_users')
    
    if not azure_handler or not table_name:
        st.error("Application initialization error. Please refresh the page.")
        return
    
    # Password update logic
    user_handler = UserHandler(azure_handler, table_name)      
    username = st.session_state['user']  
    retrieved_user = user_handler.get_user(username=username)
    
    st.title("Update Password")

    password = st.text_input("Current Password", type="password")
    newPassword1 = st.text_input("New Password", type="password")
    newPassword2 = st.text_input("Confirm New Password", type="password")

    # Load and display password requirements
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    password_file_path = os.path.join(base_dir, "res", "password", "password_text.md")

    if os.path.exists(password_file_path):
        with open(password_file_path, 'r') as password_file:
            password_text = password_file.read()
            st.info(password_text)
    else:
        st.info("Password requirements file not found.")

    if st.button("Update Password"):
        if retrieved_user.password_hash == "":
            print("New user")
        elif not check_password(password, retrieved_user):
            st.error("Current Password is incorrect.")
            return

        if newPassword1 != "" and newPassword2 != "":
            if newPassword1 != newPassword2:
                st.error("New Password and confirmation don't match")
                return

        new_password_is_complex = check_password_complexity(retrieved_user, newPassword1)

        if not new_password_is_complex[0]:
            st.error(new_password_is_complex[1])
            return
        else:
            user_handler = UserHandler(azure_handler, table_name) 
            password_hash = hash_password(newPassword1)
            user_handler.update_password(username, password_hash)
            st.session_state["password_expired"] = False
            # Navigation will be handled automatically by st.navigation
            st.rerun()