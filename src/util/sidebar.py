import datetime
import os
import streamlit as st

from config.settings import Settings
from util.session_manager import SessionManager

def sidebar(settings: Settings = None):
    # Create settings for shared resources if not provided
    if settings is None:
        settings = Settings()  # No session_id needed for shared resources

    logo = os.path.join(settings.RES_IMG_DIR, "capgemini_logo.png")
    st.logo(logo)

    with st.sidebar:
        if not SessionManager.is_authenticated():
            return
        
        user_engagement = st.session_state["user_engagement"]
        username: str = st.session_state['user']
        is_admin = st.session_state['is_admin']

        st.markdown("### Account Information")
        st.markdown(f"**Username:** {username}")
        st.markdown(f"**Engagement:** {user_engagement}")


