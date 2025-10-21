"""Main page wrapper for st.navigation"""
import streamlit as st

def main_page_wrapper():
    """Main page wrapper function"""
    # Add sidebar
    from util.sidebar import sidebar
    sidebar()
    
    # Get handlers from session state
    azure_handler = st.session_state.get('azure_handler')
    table_name = st.session_state.get('table_name_users')
    
    if not azure_handler or not table_name:
        st.error("Application initialization error. Please refresh the page.")
        return
    
    # Import and call the existing main_page function
    from main import main_page
    main_page(azure_handler, table_name)