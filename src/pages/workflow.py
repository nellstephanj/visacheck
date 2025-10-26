"""Visa Agent Workflow Page"""
import streamlit as st
import json
from datetime import datetime
from util.session_manager import SessionManager


def render_visual_workflow(steps, workflow_state):
    """Render the visual workflow with circles and arrows"""
    
    # CSS for animations and styling
    st.markdown("""
    <style>
    .workflow-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 20px 0;
        margin: 20px 0;
    }
    
    .workflow-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 0 10px;
        min-width: 80px;
        flex-shrink: 0;
    }
    
    .step-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        position: relative;
        flex-shrink: 0;
        vertical-align: top;
    }
    
    .step-pending {
        background-color: #e0e0e0;
        color: #666;
        border: 2px solid #ccc;
    }
    
    .step-processing {
        background-color: #2196F3;
        color: white;
        border: 2px solid #1976D2;
        animation: pulse 1.5s infinite;
    }
    
    .step-completed {
        background-color: #4CAF50;
        color: white;
        border: 2px solid #388E3C;
    }
    
    .step-name {
        font-size: 12px;
        text-align: center;
        font-weight: 500;
        color: #333;
        max-width: 80px;
        word-wrap: break-word;
    }
    
    .workflow-arrow {
        font-size: 20px;
        color: #666;
        margin: 0 5px;
        align-self: center;
        margin-top: 30px;
        flex-shrink: 0;
    }
    
    .spinning {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(33, 150, 243, 0); }
        100% { box-shadow: 0 0 0 0 rgba(33, 150, 243, 0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Build workflow HTML
    workflow_html = '<div class="workflow-container">'
    
    for i, step in enumerate(steps):
        state = workflow_state['step_states'][i]
        
        # Determine circle class and content
        if state == 'pending':
            circle_class = 'step-pending'
            content = step['icon']
        elif state == 'processing':
            circle_class = 'step-processing'
            content = '<span class="spinning">⟲</span>'
        else:  # completed
            circle_class = 'step-completed'
            content = '✓'
        
        # Add step
        workflow_html += f'''
        <div class="workflow-step">
            <div class="step-circle {circle_class}">
                {content}
            </div>
            <div class="step-name">{step['name']}</div>
        </div>
        '''
        
        # Add arrow (except after last step)
        if i < len(steps) - 1:
            workflow_html += '<div class="workflow-arrow">→</div>'
    
    workflow_html += '</div>'
    
    # Render the workflow
    st.markdown(workflow_html, unsafe_allow_html=True)


def workflow_page():
    """Sexy Visa Agent Workflow Page"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Get application data from query params
    if 'workflow_app_data' not in st.session_state:
        st.error("No application data found. Please return to Active Applications.")
        if st.button("← Back to Active Applications"):
            st.switch_page("pages/active_applications.py")
        return
    
    application = st.session_state['workflow_app_data']
    
    # Page title
    st.title(f"🤖 Sexy Visa Agent - {application['application_number']}")
    
    # Application details section
    st.markdown("### Application Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Application Number:** {application['application_number']}")
        st.markdown(f"**Case Type:** {application['case_type']}")
        st.markdown(f"**Visa Type:** {application['visa_type_requested']}")
        st.markdown(f"**Submission Date:** {application['submission_date']}")
    
    with col2:
        st.markdown(f"**Nationality:** {application['nationality']}")
        st.markdown(f"**Intake Location:** {application['intake_location']}")
        st.markdown(f"**Days in Process:** {application['days_in_process']}")
        urgent_status = "🔴 Yes" if application['urgent'] else "No"
        st.markdown(f"**Urgent:** {urgent_status}")
    
    st.divider()
    
    # Workflow section
    st.markdown("### Workflow Progress")
    
    # Initialize workflow state
    workflow_key = f"workflow_{application['application_number']}"
    if f"{workflow_key}_state" not in st.session_state:
        st.session_state[f"{workflow_key}_state"] = {
            'current_step': 0,
            'step_states': ['pending'] * 5,  # pending, processing, completed
            'is_running': False,
            'all_completed': False
        }
    
    workflow_state = st.session_state[f"{workflow_key}_state"]
    
    # Workflow steps configuration
    steps = [
        {'icon': '📄', 'name': 'Verify Docs'},
        {'icon': '👆', 'name': 'Check Biometrics'},
        {'icon': '🔍', 'name': 'EU VIS Check'},
        {'icon': '✓', 'name': 'Validate Info'},
        {'icon': '✅', 'name': 'Final Review'}
    ]
    
    # Create visual workflow
    render_visual_workflow(steps, workflow_state)
    
    st.write("")
    
    # Control buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.info("👈 Use the sidebar to navigate back to Active Applications")
    
    with col2:
        reset_disabled = not any(state != 'pending' for state in workflow_state['step_states'])
        if st.button("Reset", use_container_width=True, disabled=reset_disabled):
            workflow_state['current_step'] = 0
            workflow_state['step_states'] = ['pending'] * 5
            workflow_state['is_running'] = False
            workflow_state['all_completed'] = False
            st.rerun()
    
    with col3:
        start_disabled = workflow_state['is_running'] or workflow_state['all_completed']
        if st.button("Start Workflow", type="primary", use_container_width=True, disabled=start_disabled):
            workflow_state['is_running'] = True
            workflow_state['current_step'] = 0
            workflow_state['step_states'][0] = 'processing'
    
    # Auto-advance workflow steps using timer
    if workflow_state['is_running'] and not workflow_state['all_completed']:
        current_step = workflow_state['current_step']
        
        # Initialize step start time if not set
        step_timer_key = f"{workflow_key}_step_{current_step}_start"
        if step_timer_key not in st.session_state:
            st.session_state[step_timer_key] = datetime.now()
        
        # Check if step processing time has elapsed (2 seconds)
        step_start_time = st.session_state[step_timer_key]
        elapsed_time = (datetime.now() - step_start_time).total_seconds()
        
        if elapsed_time >= 2.0 and workflow_state['step_states'][current_step] == 'processing':
            # Complete current step
            workflow_state['step_states'][current_step] = 'completed'
            
            # Remove the timer for this step
            del st.session_state[step_timer_key]
            
            # Move to next step
            if current_step < 4:
                workflow_state['current_step'] += 1
                workflow_state['step_states'][current_step + 1] = 'processing'
                st.rerun()
            else:
                # All steps completed
                workflow_state['is_running'] = False
                workflow_state['all_completed'] = True
                st.success("🎉 All workflow steps completed successfully!")
                st.balloons()
        elif workflow_state['step_states'][current_step] == 'processing':
            # Still processing, auto-refresh every second
            st.rerun()
    
    # Show progress message when running
    if workflow_state['is_running']:
        current_step_name = steps[workflow_state['current_step']]['name']
        st.info(f"🔄 Processing: {current_step_name}...")
        
    # Display completion status
    if workflow_state['all_completed']:
        st.success("✅ All workflow steps completed!")
        
        # Additional completion actions
        st.markdown("### Next Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Generate Report", use_container_width=True):
                st.info("Report generation feature coming soon!")
        
        with col2:
            if st.button("📧 Send Notification", use_container_width=True):
                st.info("Notification feature coming soon!")
        
        with col3:
            if st.button("📁 Archive Application", use_container_width=True):
                st.info("Archive feature coming soon!")
    
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
            "📚 Workflow Guidelines",
            "https://example.com/workflow-guidelines",
            type="secondary",
            use_container_width=True
        )