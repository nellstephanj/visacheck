"""Admin page for st.navigation"""
import streamlit as st

from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.sidebar import sidebar

# Import admin modules from app_pages
from app_pages.admin.user_management import user_management_section, get_users_for_engagement
from app_pages.admin.engagement_management import manage_engagements_section, get_engagements
from app_pages.admin.session_monitor import session_monitor_section
from app_pages.admin.usage_monitor import usage_monitor_section

def admin_page():
    """Admin page function"""
    # Add sidebar
    sidebar()
    
    # Get handlers from session state
    user_handler = st.session_state.get('user_handler')
    azure_handler = st.session_state.get('azure_handler')
    
    if not user_handler or not azure_handler:
        st.error("Application initialization error. Please refresh the page.")
        return
    
    # Main admin page logic
    engagements = get_engagements(azure_handler)
    
    st.title("Admin Panel")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["User Management", "Manage Engagements", "Session Monitor", "Usage Monitor"])
    
    with tab1:
        user_management_section(user_handler, engagements)
    
    with tab2:
        manage_engagements_section(user_handler, azure_handler)
    
    with tab3:
        session_monitor_section()
    
    with tab4:
        usage_monitor_section(azure_handler, get_engagements)
    
    # Display current engagements for reference
    st.divider()
    st.subheader("System Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Users", len(get_users_for_engagement(user_handler)))
    
    with col2:
        st.metric("Total Engagements", len(engagements))