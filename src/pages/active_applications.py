"""Active Applications Page"""
import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime
from util.session_manager import SessionManager
from config.settings import Settings


def load_person_data(file_path):
    """Load person data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def calculate_days_in_process(submission_date_str):
    """Calculate days since submission"""
    try:
        submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
        today = datetime.now()
        days = (today - submission_date).days
        return days
    except Exception as e:
        raise ValueError(f"Unable to calculate days in process: invalid date format '{submission_date_str}'. Expected format: YYYY-MM-DD") from e


def get_days_color(days):
    """Get color based on days in process"""
    if days > 30:
        return "red"
    elif days > 15:
        return "orange"
    else:
        return "green"


def get_days_circle_html(days):
    """Generate HTML for days circle with color"""
    color = get_days_color(days)
    
    # Color mapping
    color_map = {
        "red": "#FF4444",
        "orange": "#FF9800", 
        "green": "#4CAF50"
    }
    
    bg_color = color_map.get(color, "#4CAF50")
    
    html = f"""
    <div style="
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: {bg_color};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
        margin: 0 auto;
    ">
        {days}
    </div>
    """
    return html


def get_people_files(people_dir):
    """Get all people files sorted by filename"""
    files = list(Path(people_dir).glob("person_*.json"))
    # Sort by filename for consistent ordering instead of random shuffle
    files.sort(key=lambda f: f.name)
    return files


def get_total_applications_count(people_dir):
    """Get total count of applications for display"""
    files = get_people_files(people_dir)
    return len(files)


def get_applications_page(people_dir, page_number=1, per_page=25):
    """Get applications for a specific page"""
    files = get_people_files(people_dir)
    start_idx = (page_number - 1) * per_page
    end_idx = start_idx + per_page
    page_files = files[start_idx:end_idx]
    
    applications = []
    for file_path in page_files:
        person_data = load_person_data(file_path)
        
        # Calculate days in process
        submission_date_str = person_data.get('submission_date')
        if not submission_date_str:
            continue
            
        days_in_process = calculate_days_in_process(submission_date_str)
        submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
        
        # Random application status
        status_options = ['To Decide', 'Ready for Matching', 'To Consult', 'Rolled Back', 'Awaiting Approval']
        
        application = {
            'submission_date': submission_date.strftime("%d/%m/%Y"),
            'days_in_process': days_in_process,
            'application_number': person_data.get('visa_application_number', 'N/A'),
            'intake_location': person_data.get('intake_location', 'N/A'),
            'application_status': random.choice(status_options),
            'urgent': person_data.get('urgent', False),
            'case_type': person_data.get('case_type', 'N/A'),
            'visa_type_requested': person_data.get('visa_type_requested', 'N/A'),
            'nationality': person_data.get('country_of_nationality', 'N/A'),
            'person_data': person_data
        }
        applications.append(application)
    
    # Sort by days in process (descending - oldest first)
    applications.sort(key=lambda x: x['days_in_process'], reverse=True)
    
    return applications


def active_applications_page():
    """Active Applications List Page"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Page title
    st.title("Active Applications")
    
    # Get the people directory from settings
    settings = Settings()
    people_dir = settings.PEOPLE_DIR
    
    # Get total count for display
    total_count = get_total_applications_count(people_dir)
    
    # Pagination setup
    per_page = 25
    total_pages = (total_count + per_page - 1) // per_page
    
    # Initialize page number in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Display total count
    st.write(f"**Total Applications:** {total_count}")
    
    # Pagination controls
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col1:
        if st.button("← Previous", disabled=st.session_state.current_page <= 1):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.write(f"Page {st.session_state.current_page} of {total_pages}")
    
    with col3:
        st.write(f"Showing {min(per_page, total_count - (st.session_state.current_page - 1) * per_page)} of {total_count} applications")
    
    with col4:
        if st.button("Next →", disabled=st.session_state.current_page >= total_pages):
            st.session_state.current_page += 1
            st.rerun()
    
    st.divider()
    
    # Get applications for current page
    try:
        applications = get_applications_page(people_dir, st.session_state.current_page, per_page)
    except Exception as e:
        st.error(f"Error loading applications: {str(e)}")
        return
    
    if not applications:
        st.info("No applications found on this page.")
        return
    
    # Create table header
    header_cols = st.columns([1.2, 1, 1.5, 1.2, 1.2, 0.8, 1.2, 1.2, 1.2, 1.5])
    headers = [
        "Submission Date",
        "Days in Process", 
        "Application Number",
        "Intake Location",
        "Application Status",
        "Urgent",
        "Case Type",
        "Visa Type Requested",
        "Nationality",
        "Action"
    ]
    
    for col, header in zip(header_cols, headers):
        col.markdown(f"**{header}**")
    
    st.markdown("---")
    
    # Display applications
    for idx, app in enumerate(applications):
        cols = st.columns([1.2, 1, 1.5, 1.2, 1.2, 0.8, 1.2, 1.2, 1.2, 1.5])
        
        # Submission Date
        with cols[0]:
            st.write(app['submission_date'])
        
        # Days in Process (with colored circle)
        with cols[1]:
            days = app['days_in_process']
            st.markdown(get_days_circle_html(days), unsafe_allow_html=True)
        
        # Application Number
        with cols[2]:
            st.write(app['application_number'])
        
        # Intake Location
        with cols[3]:
            st.write(app['intake_location'])
        
        # Application Status (with badge)
        with cols[4]:
            st.markdown(f"""
                <div style='background-color: #00BCD4; padding: 4px 8px; 
                            border-radius: 4px; text-align: center; color: white;
                            font-size: 12px; font-weight: bold;'>
                    {app['application_status']}
                </div>
            """, unsafe_allow_html=True)
        
        # Urgent
        with cols[5]:
            if app['urgent']:
                st.markdown("🔴 **Yes**")
            else:
                st.write("No")
        
        # Case Type
        with cols[6]:
            st.write(app['case_type'])
        
        # Visa Type Requested
        with cols[7]:
            st.write(app['visa_type_requested'])
        
        # Nationality
        with cols[8]:
            st.write(app['nationality'])
        
        # Action Button
        with cols[9]:
            # Use application number as unique key instead of index
            button_key = f"execute_{app['application_number']}"
            if st.button("🤖 Agent", key=button_key, use_container_width=True):
                # Store application data in session state for workflow page
                st.session_state['workflow_app_data'] = app
                st.session_state[f'show_success_{app["application_number"]}'] = True
                st.rerun()
        
        st.markdown("---")
        
        # Show success message underneath the row if button was clicked
        if st.session_state.get(f'show_success_{app["application_number"]}', False):
            st.success(f"✅ Agent loaded for {app['application_number']}! Click the 🤖 Sexy Visa Agent tab in the sidebar to continue.")
            # Clear the success message flag
            if f'show_success_{app["application_number"]}' in st.session_state:
                del st.session_state[f'show_success_{app["application_number"]}']
        
    
    # Bottom pagination
    st.divider()
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col1:
        if st.button("← Prev", disabled=st.session_state.current_page <= 1, key="bottom_prev"):
            st.session_state.current_page -= 1
            st.rerun()
    
    with col2:
        st.write(f"Page {st.session_state.current_page} of {total_pages}")
    
    with col3:
        st.write(f"Applications {(st.session_state.current_page - 1) * per_page + 1}-{min(st.session_state.current_page * per_page, total_count)} of {total_count}")
    
    with col4:
        if st.button("Next →", disabled=st.session_state.current_page >= total_pages, key="bottom_next"):
            st.session_state.current_page += 1
            st.rerun()
    
    # Help section
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button(
            "✉️ Mail Support",
            "mailto:support@visacheck.com",
            type="secondary",
            use_container_width=True
        )
    
    with col2:
        st.link_button(
            "📚 Application Guidelines",
            "https://example.com/guidelines",
            type="secondary",
            use_container_width=True
        )


