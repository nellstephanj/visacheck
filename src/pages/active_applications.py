"""Active Applications Page"""
import streamlit as st
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from util.session_manager import SessionManager


def load_person_data(file_path):
    """Load person data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def get_random_people(people_dir, count=20):
    """Get random people from the people directory"""
    json_files = list(Path(people_dir).glob("person_*.json"))
    selected_files = random.sample(json_files, min(count, len(json_files)))
    return [load_person_data(file) for file in selected_files]


def calculate_days_in_process(submission_date_str):
    """Calculate days since submission"""
    try:
        submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
        today = datetime.now()
        days = (today - submission_date).days
        return days
    except:
        return random.randint(-5, 30)


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


def generate_mock_applications(people):
    """Generate mock application data from people"""
    applications = []
    
    offices = [
        "Kai e2e Registration officer 9",
        "Kai e2e Registration officer 5",
        "Kai e2e Registration officer 3",
        "Kai e2e Registration officer 7",
        None  # For unassigned
    ]
    
    group_names = ["Nguyen", "Johnson", "Smith", "Garcia", "Martinez", "Chen"]
    
    for idx, person in enumerate(people):
        # Calculate submission date (random between 0-40 days ago)
        days_ago = random.randint(0, 40)
        submission_date = datetime.now() - timedelta(days=days_ago)
        
        # Group size (2-5 people)
        group_size = random.randint(2, 5)
        
        application = {
            'id': idx + 1,
            'submission_date': submission_date.strftime("%d/%m/%Y"),
            'submission_date_iso': submission_date.strftime("%Y-%m-%d"),
            'days_in_process': days_ago,
            'application_number': person.get('visa_application_number', f'NLDMFAZ30599854234{idx:04d}'),
            'group_size': group_size,
            'group_name': random.choice(group_names),
            'intake_location': person.get('intake_location', 'Abu Dhabi-FO'),
            'application_status': 'To Decide',
            'date_of_arrival': (datetime.now() + timedelta(days=random.randint(5, 30))).strftime("%d/%m/%Y"),
            'nationality': person.get('country_of_nationality', 'Unknown'),
            'assigned_user': random.choice(offices),
            'person_data': person
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
    
    # Action buttons at the top
    col1, col2, col3 = st.columns([1, 1, 4])
    with col2:
        if st.button("Assign", type="primary", use_container_width=True):
            st.info("Assign functionality coming soon")
    with col1:
        if st.button("Unassign", use_container_width=True):
            st.info("Unassign functionality coming soon")
    
    st.divider()
    
    # Get the people directory
    base_dir = Path(__file__).parent.parent.parent
    people_dir = base_dir / "res" / "people"
    
    # Initialize session state for applications
    if 'active_applications' not in st.session_state:
        people = get_random_people(people_dir, count=20)
        st.session_state['active_applications'] = generate_mock_applications(people)
        st.session_state['selected_applications'] = []
    
    applications = st.session_state.get('active_applications', [])
    
    # Tabs for Active and Pending
    tab1, tab2 = st.tabs(["Active", "Pending"])
    
    with tab1:
        st.markdown("### Active Applications List")
        st.write("")
        
        # Create table header
        header_cols = st.columns([0.5, 1, 1.2, 1.5, 1, 1, 1.2, 1, 1.2, 1.5, 1.5, 1.8])
        headers = [
            "",  # Checkbox
            "Submission Date",
            "Days in Process",
            "Application Number",
            "Group Size",
            "Group Name",
            "Intake Location",
            "Application Status",
            "Date of Arrival",
            "Nationality",
            "Assigned User",
            "Action"
        ]
        
        for col, header in zip(header_cols, headers):
            col.markdown(f"**{header}**")
        
        st.markdown("---")
        
        # Display applications
        for app in applications:
            cols = st.columns([0.5, 1, 1.2, 1.5, 1, 1, 1.2, 1, 1.2, 1.5, 1.5, 1.8])
            
            # Checkbox
            with cols[0]:
                checkbox_key = f"app_check_{app['id']}"
                is_checked = st.checkbox("", key=checkbox_key, label_visibility="collapsed")
                if is_checked and app['id'] not in st.session_state['selected_applications']:
                    st.session_state['selected_applications'].append(app['id'])
                elif not is_checked and app['id'] in st.session_state['selected_applications']:
                    st.session_state['selected_applications'].remove(app['id'])
            
            # Submission Date
            with cols[1]:
                st.write(app['submission_date'])
            
            # Days in Process (with colored circle)
            with cols[2]:
                days = app['days_in_process']
                st.markdown(get_days_circle_html(days), unsafe_allow_html=True)
            
            # Application Number
            with cols[3]:
                st.write(app['application_number'])
            
            # Group Size (with icon)
            with cols[4]:
                st.markdown(f"👥 {app['group_size']}")
            
            # Group Name
            with cols[5]:
                st.write(app['group_name'])
            
            # Intake Location
            with cols[6]:
                st.write(app['intake_location'])
            
            # Application Status (with badge)
            with cols[7]:
                st.markdown(f"""
                    <div style='background-color: #00BCD4; padding: 4px 8px; 
                                border-radius: 4px; text-align: center; color: white;
                                font-size: 12px; font-weight: bold;'>
                        {app['application_status']}
                    </div>
                """, unsafe_allow_html=True)
            
            # Date of Arrival
            with cols[8]:
                st.write(app['date_of_arrival'])
            
            # Nationality
            with cols[9]:
                st.write(app['nationality'])
            
            # Assigned User
            with cols[10]:
                if app['assigned_user']:
                    st.write(app['assigned_user'])
                else:
                    st.markdown("*UnAssigned*")
            
            # Action Button
            with cols[11]:
                if st.button("Execute Agent Workflow", key=f"execute_{app['id']}", use_container_width=True):
                    show_workflow_modal(app)
            
            st.markdown("---")
        
        # Show count
        st.write(f"**Total Active Applications:** {len(applications)}")
    
    with tab2:
        st.info("Pending applications will be displayed here")
    
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


def show_workflow_modal(application):
    """Show modal for agent workflow execution"""
    @st.dialog(f"🤖 Agent Workflow - {application['application_number']}", width="large")
    def workflow_dialog():
        st.markdown("### Application Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Application Number:** {application['application_number']}")
            st.markdown(f"**Group Name:** {application['group_name']}")
            st.markdown(f"**Group Size:** 👥 {application['group_size']}")
            st.markdown(f"**Submission Date:** {application['submission_date']}")
        
        with col2:
            st.markdown(f"**Nationality:** {application['nationality']}")
            st.markdown(f"**Intake Location:** {application['intake_location']}")
            st.markdown(f"**Days in Process:** {application['days_in_process']}")
            st.markdown(f"**Status:** {application['application_status']}")
        
        st.divider()
        
        st.markdown("### Workflow Actions")
        
        # Workflow steps
        workflows = [
            "🔍 Verify Documents",
            "👤 Check Biometrics",
            "🌍 EU-VIS Matching",
            "📋 Validate Information",
            "✅ Final Review"
        ]
        
        st.write("Select workflow steps to execute:")
        
        selected_workflows = []
        for workflow in workflows:
            if st.checkbox(workflow, value=True, key=f"wf_{workflow}"):
                selected_workflows.append(workflow)
        
        st.write("")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("Execute", type="primary", use_container_width=True):
                if selected_workflows:
                    st.success(f"✅ Executing {len(selected_workflows)} workflow step(s)...")
                    st.balloons()
                    # Here you would trigger the actual workflow
                else:
                    st.warning("Please select at least one workflow step")
    
    workflow_dialog()
