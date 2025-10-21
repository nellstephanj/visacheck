"""
User Management Module
Handles user creation, management, and related operations
"""

import streamlit as st
from typing import Optional

from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.user import validate_email_format
from util.auth_functions import hash_password


def get_users_for_engagement(user_handler: UserHandler, engagement: Optional[str] = None):
    """Get users for specific engagement or all users"""
    return user_handler.get_engagement_users(engagement)


def delete_user_from_database(user_handler: UserHandler, email):
    """
    Function to delete user from database.
    For now removes from mock data - implement database logic here later.
    """
    user_handler.delete_user(email)
    return True


def user_management_section(user_handler: UserHandler, engagements):
    """Combined user management section with create and manage functionality"""
    st.header("User Management")
    
    # Add user section at the top
    st.subheader("Add New User")
    
    email = st.text_input("User email")
    temp_password = st.text_input("User password", type="password")
    
    # Simple engagement selection dropdown
    engagement = st.selectbox(
        "Select engagement",
        options=engagements,
        index=None,
        placeholder="Choose an engagement..."
    )
    
    is_admin = st.checkbox("Give user admin rights")
    
    # Create user button
    if st.button("Create User", key="create_user_btn"):
        if not validate_email_format(email):
            st.error("Please enter a correct email address")
        elif email and email.strip() and user_handler.get_user(email):
            st.error("User already exists")
        elif len(temp_password) < 8:
            st.error("Please enter a password using more than 8 characters")
        elif not engagement:
            st.error("Please select an engagement")
        else:
            user_handler.create_and_save_user(
                username=email, 
                email=email, 
                password_hash=hash_password(temp_password), 
                engagement=engagement, 
                is_admin=is_admin
            )
            st.success("User successfully added!")
    
    st.divider()
    
    # User overview section
    st.subheader("User Overview")
    
    # Get users data
    users_data = get_users_for_engagement(user_handler)
    
    if not users_data:
        st.info("No users found in the system.")
        return
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        engagement_filter = st.selectbox(
            "Filter by engagement",
            options=["All"] + engagements,
            index=0,
            key="engagement_filter"
        )
    
    with col2:
        st.write("")  # Empty space for alignment
    
    # Filter users based on engagement selection
    if engagement_filter == "All":
        filtered_users = get_users_for_engagement(user_handler)
    else:
        filtered_users = get_users_for_engagement(user_handler, engagement_filter)
    
    if not filtered_users:
        st.info(f"No users found for engagement: {engagement_filter}")
        return
    
    st.write(f"Showing {len(filtered_users)} user(s)")
    
    # Create table with user data
    for i, user in enumerate(filtered_users):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1.5, 1])
            
            with col1:
                st.write(f"**{user['email']}**")
            
            with col2:
                st.write(user['engagement'])
            
            with col3:
                admin_status = "Admin" if user['is_admin'] else "User"
                if user['is_admin']:
                    st.write(f"🔑 {admin_status}")
                else:
                    st.write(f"👤 {admin_status}")
            
            with col4:
                # Delete button
                if st.button("Delete", key=f"delete_{i}_{user['email']}", type="secondary"):
                    if delete_user_from_database(user_handler, user['email']):
                        st.success(f"User {user['email']} deleted successfully!")
                        st.rerun()  # Refresh the page to update the table
            
            st.divider()