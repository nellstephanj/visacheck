"""
Engagement Management Module
Handles engagement creation, management, and related operations
"""

import streamlit as st

from util.azure_functions import AzureHandler
from util.user_functions import UserHandler


def get_engagements(azure_handler: AzureHandler) -> list[str]:
    """Get list of all engagements from Azure table"""
    engagement_entities = azure_handler.retrieve_table_items("Engagements")
    if not engagement_entities:
        return []
    
    engagement_list = list(engagement_entities)
    engagements = [entity.get("RowKey") for entity in engagement_list if entity and entity.get("RowKey")]
    return engagements


def add_engagement_to_database(azure_handler: AzureHandler, new_engagement: str):
    """Add new engagement to database"""
    new_entity = {
        'PartitionKey': 'EngagementPartition',
        'RowKey': new_engagement
    }
    azure_handler.insert_entity('Engagements', new_entity)
    return True


def delete_engagement_from_database(azure_handler: AzureHandler, engagement_name):
    """Delete engagement from database"""
    azure_handler.delete_entity(table_name='Engagements', partition_key='EngagementPartition', row_key=engagement_name)
    return True


def get_users_for_engagement(user_handler: UserHandler, engagement: str = None):
    """Get users for specific engagement"""
    return user_handler.get_engagement_users(engagement)


def manage_engagements_section(user_handler: UserHandler, azure_handler: AzureHandler):
    """Manage Engagements tab functionality"""
    st.header("Manage Engagements")
    
    # Display current engagements
    st.subheader("Current Engagements")
    engagements = get_engagements(azure_handler)

    if len(engagements) >= 1:
        cols = st.columns(min(len(engagements), 4))  # Max 4 columns
        for i, engagement in enumerate(engagements):
            with cols[i % 4]:
                st.info(f"📋 {engagement}")
    else:
        st.info("No engagements found.")
    
    st.divider()
    
    # Add new engagement
    st.subheader("Add New Engagement")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_engagement = st.text_input(
            "Engagement name", 
            key="new_engagement_input",
            placeholder="Enter new engagement name..."
        )
    
    with col2:
        st.write("")  # Space for alignment
        if st.button("Add Engagement", key="add_engagement_btn", type="primary"):
            if new_engagement and new_engagement.strip():
                engagement_name = new_engagement.strip().upper()
                if engagement_name in engagements:
                    st.error(f"Engagement '{engagement_name}' already exists!")
                else:
                    if add_engagement_to_database(azure_handler, engagement_name):
                        st.success(f"Engagement '{engagement_name}' added successfully!")
                        st.rerun()  # Refresh the page to show the new engagement
                    else:
                        st.error("Failed to add engagement")
            else:
                st.error("Please enter a valid engagement name")
    
    st.divider()
    
    # Delete engagement section
    st.subheader("Delete Engagement")
    st.warning("⚠️ Deleting an engagement will affect all users assigned to it.")
    
    if engagements:
        engagement_to_delete = st.selectbox(
            "Select engagement to delete",
            options=engagements,
            index=None,
            placeholder="Choose an engagement to delete...",
            key="delete_engagement_select"
        )
        
        if engagement_to_delete:
            # Check if any users are using this engagement
            users_with_engagement = [user for user in get_users_for_engagement(user_handler, engagement_to_delete) if user["engagement"] == engagement_to_delete]
            
            if users_with_engagement:
                st.error(f"Cannot delete '{engagement_to_delete}' - {len(users_with_engagement)} user(s) are assigned to this engagement.")
                st.write("Users with this engagement:")
                for user in users_with_engagement:
                    st.write(f"• {user['email']}")
            else:
                if st.button("Delete Engagement", key="delete_engagement_btn", type="secondary"):
                    if delete_engagement_from_database(azure_handler, engagement_to_delete):
                        st.success(f"Engagement '{engagement_to_delete}' deleted successfully!")
                        st.rerun()  # Refresh the page
                    else:
                        st.error("Failed to delete engagement")
    else:
        st.info("No engagements available to delete.")