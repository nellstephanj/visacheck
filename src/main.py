import streamlit as st
import time
import os

from dotenv import load_dotenv

st.set_page_config(
    page_title="VisaCheck",
    page_icon=os.path.join(os.path.dirname(__file__), "Favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

from config.settings import Settings

from util.session_manager import SessionManager
from util.session_cleanup import SessionCleanup
from util.video_trimmer_functions import VideoTrimmerHandler
from util.logging_functions import LoggingHandler
from util.docx_functions import DocumentHandler
from util.azure_openai_functions import OpenAIHandler
from util.manual_functions import ManualHandler
from util.file_functions import ProcessedFile
from util.azure_functions import AzureHandler
from util.user_functions import UserHandler
from util.auth_functions import AuthHandler
from util.progress_tracker import VideoProgressTracker

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

    # Instantiate settings class with session-specific directories
    settings = Settings(session_id=st.session_state['session_id'])

    # Initialize handlers (caching is now handled inside each handler)
    table_name_logs = os.getenv("TABLE_NAME_LOGS")
    if table_name_logs is None:
        st.error("Unable to retrieve logs table name")
        return
        
    logging_handler = LoggingHandler(azure_handler, table_name_logs)
    # OpenAI handler now uses internal caching for Key Vault calls
    openai_handler = OpenAIHandler(azure_handler, logging_handler, settings)

    st.title('VisaCheck')

    uploaded_files = st.file_uploader("Choose files to upload", type=["docx", "pdf", "txt", "mp4", "png"], accept_multiple_files=True)

    # Video segment selection using the VideoTrimmerHandler
    video_segment = None
    if uploaded_files:
        video_segment = VideoTrimmerHandler.handle_video_upload(uploaded_files, settings)

    # Prompt selection radio buttons
    input_prompt = st.radio("Choose the kind of documentation:", ["Manual", "Summary"], index=0, horizontal=True)
    input_prompt_code = "Man" if input_prompt == "Manual" else "Sum"

    # Language selection radio buttons
    input_language = st.radio("Choose the language of your source files:", ["English", "Dutch"], index=0, horizontal=True)
    input_language_code = "nl" if input_language == "Dutch" else "en"

    output_language = st.radio("Choose the language of the generated documentation:", ["English", "Dutch"], index=0, horizontal=True)
    output_language_code = "nl" if output_language == "Dutch" else "en"

    # Check button validation using VideoTrimmerHandler
    video_segment_valid, help_message = VideoTrimmerHandler.check_button_validation(uploaded_files or [])

    # Create Documentation button with conditional disabling
    is_processing = st.session_state.get('is_processing', False)
    button_disabled = (not video_segment_valid) or is_processing
    
    process_button = st.button(
        "Create Documentation", 
        type="primary", 
        width="stretch",
        disabled=button_disabled,
        help=help_message
    )
    
    # Container for output
    with st.container(border=True):

        if uploaded_files and process_button:
            # Set processing state immediately and rerun to update UI
            st.session_state['is_processing'] = True
            st.rerun()
            
        if uploaded_files and st.session_state.get('is_processing', False):
            # Update activity when user starts processing
            SessionManager.update_activity()
            
            # Every time the process_button is pressed, we clean out the processed_files in session_state.
            st.session_state['processed_files'] = []

            start_time = time.time()
            includes_video = False
            
            # Divider and space between buttons and generated text
            st.subheader("Output")
            st.divider()
            
            # Initialize progress tracking for video files
            video_files = [f for f in uploaded_files if f.type == "video/mp4"]
            if video_files:
                progress_tracker = VideoProgressTracker()
                progress_tracker.initialize()
                st.session_state['progress_tracker'] = progress_tracker
            else:
                # Clear any existing progress tracker for non-video files
                st.session_state['progress_tracker'] = None
            
            for uploaded_file in uploaded_files:
                # Reset file pointer before processing
                uploaded_file.seek(0)
                
                processed_file : ProcessedFile = ManualHandler.extract_text_from_file(
                    uploaded_file, 
                    openai_handler, 
                    input_language_code, 
                    output_language_code,
                    settings,
                    video_segment=video_segment if uploaded_file.type == "video/mp4" else None
                )
                if processed_file.extracted_text:
                    st.session_state['processed_files'].append(processed_file)
            
            if st.session_state['processed_files']:
                manual_text_container = st.empty()
                manual_text = ""
                
                # Selecting the right prompt
                includes_video = any(pf.file_type == "video" for pf in st.session_state['processed_files'])

                # Determine which prompt file to use based on both video presence and user selection
                if input_prompt_code == "Man":  # Manual
                    prompt_file_to_use = os.path.join(settings.PROMPT_DIR, "main_prompt_timestamps.txt") if includes_video else os.path.join(settings.PROMPT_DIR, "main_prompt.txt")
                else:  # Summary
                    prompt_file_to_use = os.path.join(settings.PROMPT_DIR, "second_prompt_timestamps.txt") if includes_video else os.path.join(settings.PROMPT_DIR, "second_prompt.txt")

                print("Using the following prompt:")
                print(prompt_file_to_use)
                
                # Step 4: Manual Generation
                progress_tracker = st.session_state.get('progress_tracker')
                if progress_tracker and includes_video:
                    progress_tracker.update_step(3)
                
                # Streaming the reply
                for chunk in openai_handler.create_manual_based_on_multiple_files(st.session_state['processed_files'], prompt_file_to_use, output_language_code):
                    manual_text += chunk
                    manual_text_container.write(manual_text)

                display_text = manual_text
                image_paths = {}

                if includes_video:
                    # Step 5: Screenshot Extraction
                    if progress_tracker:
                        progress_tracker.update_step(4)
                    
                    # Retrieve the first video_path of processed_files with type "video"
                    video_path = next((pf.video_path for pf in st.session_state['processed_files'] if pf.file_type == "video"), None)
                    
                    # Step 6: Placeholder Replacement  
                    if progress_tracker:
                        progress_tracker.update_step(5)
                    
                    display_text, manual_text, image_paths = ManualHandler.replace_placeholders_with_screenshots(manual_text, video_path, settings, video_segment)
                    manual_text_container.markdown(display_text, unsafe_allow_html=True)
                    
                    # Complete progress
                    if progress_tracker:
                        progress_tracker.complete()
                else:
                    manual_text_container.markdown(manual_text)

                # Divider between text and download button
                st.divider()

                word_document = DocumentHandler.generate_word_document(manual_text, image_paths)
                
                # Create columns for download and start over buttons
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.download_button(
                        label="Download as Word document",
                        type="primary",
                        data=word_document,
                        file_name="Documentation.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                with col2:
                    if st.button("🔄 Start Over", type="secondary", width="stretch"):
                        # Update activity when user starts over
                        SessionManager.update_activity()
                        # Clear processed files from session state
                        st.session_state['processed_files'] = []
                        # Reset processing state
                        st.session_state['is_processing'] = False
                        st.success("✅ Ready for new files!")
                        st.rerun()

                end_time = time.time()
                total_time = end_time - start_time
                st.write(f"Total processing time: {total_time:.2f} seconds")
                ManualHandler.clear_local_folders(settings)
                
                # Reset processing state when done
                st.session_state['is_processing'] = False
                
        else:
            st.write("Please upload a file.")
    
    # Help and support section at the bottom - outside the container so it's always visible
    st.divider()
    
    # Create two columns for the buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button("✉️ Mail Support", "mailto:support@visacheck.com", type="secondary", width="stretch")
    
    with col2:
        st.link_button("🐛 Report a Bug", "mailto:support@visacheck.com", type="secondary", width="stretch")


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
            st.Page(intake_page, title="Visa Intake", icon="📋")
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