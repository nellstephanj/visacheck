import streamlit as st
import os 

from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.user import validate_email_format
from util.auth_functions import hash_password


def init_form(user_handler: UserHandler, azure_handler: AzureHandler):

    table_name_string = os.getenv("TABLE_NAMES")
    table_name_list = table_name_string.split(",") if table_name_string else print("Env variables do not split")

    st.title("Create user")

    email = st.text_input("User email")
    temp_password = st.text_input("User password")
    engagement = st.text_input("User engagement")  
    is_admin = True      

    if st.button("Create User"):

        if not validate_email_format(email):
            st.error("Please enter a correct email address")

        elif user_handler.get_user(email):
            st.error("User already exists")

        elif len(temp_password) < 8: 
            st.error("Please enter a password using more than 8 characters")      

        else: 

            # Create tables with AzureHandler
            azure_handler.create_tables(table_name_list)

            # Save user with UserHandler
            user_handler.create_and_save_user(username=email, email=email, password_hash=hash_password(temp_password), engagement=engagement, is_admin=is_admin)
            st.success("User successfully added", width="stretch")

            st.rerun()
