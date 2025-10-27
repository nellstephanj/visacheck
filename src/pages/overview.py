"""Application Overview Page - Visual Pipeline & Status Dashboard"""
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from util.session_manager import SessionManager
from config.settings import Settings
from collections import Counter


# Define the application workflow stages
WORKFLOW_STAGES = [
    {
        'id': 'unassigned',
        'name': 'New Application',
        'display': 'Unassigned',
        'icon': '📝',
        'color': '#9E9E9E',
        'description': 'Newly submitted applications awaiting intake processing',
        'ai_action': None,
        'human_action': 'Assign to case officer',
        'statuses': ['New', 'Unassigned']
    },
    {
        'id': 'intake',
        'name': 'Intake Application',
        'display': 'In Intake',
        'icon': '📋',
        'color': '#2196F3',
        'description': 'Application data being entered and validated',
        'ai_action': 'Data validation and completeness check',
        'human_action': 'Complete intake form',
        'statuses': ['Intake', 'Intake', 'Data Entry']
    },
    {
        'id': 'registered',
        'name': 'Application Registered',
        'display': 'Registered',
        'icon': '✅',
        'color': '#4CAF50',
        'description': 'Application successfully registered in system',
        'ai_action': 'Document classification and indexing',
        'human_action': 'Review registration details',
        'statuses': ['Registered', 'Submitted']
    },
    {
        'id': 'ready_for_matching',
        'name': 'Ready for Matching',
        'display': 'Ready for Match',
        'icon': '🔍',
        'color': '#FF9800',
        'description': 'Awaiting EU-VIS database matching',
        'ai_action': 'Biometric and database matching',
        'human_action': 'Initiate matching process',
        'statuses': ['Ready for Match', 'Awaiting Match', 'To Match']
    },
    {
        'id': 'verification',
        'name': 'To be Checked',
        'display': 'In Verification',
        'icon': '🔬',
        'color': '#9C27B0',
        'description': 'Document verification and fraud detection',
        'ai_action': 'Document authenticity analysis, consistency checks',
        'human_action': 'Review AI verification results',
        'statuses': ['To Consult', 'To be Checked', 'Verification', 'Under Review']
    },
    {
        'id': 'decision',
        'name': 'To Decide',
        'display': 'Decision Pending',
        'icon': '⚖️',
        'color': '#FF5722',
        'description': 'Final decision stage - approve, reject, or request more info',
        'ai_action': 'Decision recommendation with scoring',
        'human_action': 'Make final decision',
        'statuses': ['To Decide', 'Decision Pending', 'Awaiting Decision']
    },
    {
        'id': 'print',
        'name': 'To Print',
        'display': 'Ready to Print',
        'icon': '🖨️',
        'color': '#00BCD4',
        'description': 'Approved applications ready for visa printing',
        'ai_action': 'Generate visa documents',
        'human_action': 'Print and dispatch visa',
        'statuses': ['To Print', 'Print Queue', 'Awaiting Approval']
    },
    {
        'id': 'completed',
        'name': 'Completed',
        'display': 'Completed',
        'icon': '🎉',
        'color': '#4CAF50',
        'description': 'Application fully processed and closed',
        'ai_action': None,
        'human_action': 'Archive application',
        'statuses': ['Completed', 'Closed', 'Archived']
    },
    {
        'id': 'rolled_back',
        'name': 'Rolled Back',
        'display': 'Rolled Back',
        'icon': '🔄',
        'color': '#FF9800',
        'description': 'Application returned to previous stage for corrections',
        'ai_action': 'Identify issues for correction',
        'human_action': 'Review and correct issues',
        'statuses': ['Rolled Back', 'Returned', 'Revision Required']
    },
    {
        'id': 'rejected',
        'name': 'Rejected',
        'display': 'Rejected',
        'icon': '❌',
        'color': '#F44336',
        'description': 'Application declined',
        'ai_action': None,
        'human_action': 'Send rejection notice',
        'statuses': ['Rejected', 'Declined', 'Refused']
    }
]


def load_person_data(file_path):
    """Load person data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_days_in_process(submission_date_str):
    """Calculate days since submission"""
    try:
        submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
        today = datetime.now()
        days = (today - submission_date).days
        return days
    except Exception:
        return 0


def get_all_applications():
    """Load all applications from people directory"""
    settings = Settings()
    people_dir = settings.PEOPLE_DIR
    
    if not os.path.exists(people_dir):
        return []
    
    applications = []
    for filename in os.listdir(people_dir):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(people_dir, filename)
                person_data = load_person_data(file_path)
                
                submission_date_str = person_data.get('submission_date')
                if not submission_date_str:
                    continue
                
                days_in_process = calculate_days_in_process(submission_date_str)
                
                # Random status for demo
                import random
                all_statuses = []
                for stage in WORKFLOW_STAGES:
                    all_statuses.extend(stage['statuses'])
                
                application = {
                    'application_number': person_data.get('visa_application_number', 'N/A'),
                    'status': random.choice(all_statuses),
                    'submission_date': submission_date_str,
                    'days_in_process': days_in_process,
                    'urgent': person_data.get('urgent', False),
                    'case_type': person_data.get('case_type', 'N/A'),
                    'nationality': person_data.get('country_of_nationality', 'N/A'),
                    'intake_location': person_data.get('intake_location', 'N/A')
                }
                applications.append(application)
            except Exception:
                continue
    
    return applications


def map_status_to_stage(status):
    """Map application status to workflow stage"""
    for stage in WORKFLOW_STAGES:
        if status in stage['statuses']:
            return stage
    return WORKFLOW_STAGES[0]  # Default to unassigned


def get_stage_statistics(applications):
    """Calculate statistics for each stage"""
    stage_stats = {}
    
    for stage in WORKFLOW_STAGES:
        stage_apps = [app for app in applications if app['status'] in stage['statuses']]
        
        urgent_count = sum(1 for app in stage_apps if app['urgent'])
        avg_days = sum(app['days_in_process'] for app in stage_apps) / len(stage_apps) if stage_apps else 0
        overdue_count = sum(1 for app in stage_apps if app['days_in_process'] > 30)
        
        stage_stats[stage['id']] = {
            'total': len(stage_apps),
            'urgent': urgent_count,
            'avg_days': round(avg_days, 1),
            'overdue': overdue_count,
            'applications': stage_apps
        }
    
    return stage_stats


def render_pipeline_visual(stage_stats):
    """Render the visual pipeline with application counts"""
    st.markdown("### 🔄 Application Pipeline")
    
    # Create pipeline visualization
    pipeline_html = """
    <style>
        .pipeline-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
            overflow-x: auto;
            padding: 10px 0;
        }
        .stage-box {
            flex: 1;
            min-width: 120px;
            margin: 0 5px;
            padding: 15px 10px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stage-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .stage-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .stage-name {
            font-weight: bold;
            font-size: 12px;
            margin: 5px 0;
            color: white;
        }
        .stage-count {
            font-size: 28px;
            font-weight: bold;
            margin: 8px 0;
            color: white;
        }
        .stage-urgent {
            font-size: 11px;
            color: #FFE0B2;
            margin-top: 5px;
        }
        .pipeline-arrow {
            font-size: 24px;
            color: #666;
            margin: 0 -10px;
        }
    </style>
    """
    
    # Build pipeline boxes
    main_stages = [s for s in WORKFLOW_STAGES if s['id'] not in ['completed', 'rolled_back', 'rejected']]
    
    pipeline_html += '<div class="pipeline-container">'
    
    for i, stage in enumerate(main_stages):
        stats = stage_stats[stage['id']]
        
        pipeline_html += f'''
        <div class="stage-box" style="background: linear-gradient(135deg, {stage['color']}dd, {stage['color']});">
            <div class="stage-icon">{stage['icon']}</div>
            <div class="stage-name">{stage['display']}</div>
            <div class="stage-count">{stats['total']}</div>
            <div class="stage-urgent">🔴 {stats['urgent']} urgent</div>
        </div>
        '''
        
        if i < len(main_stages) - 1:
            pipeline_html += '<div class="pipeline-arrow">→</div>'
    
    pipeline_html += '</div>'
    
    st.markdown(pipeline_html, unsafe_allow_html=True)


def render_stage_details(stage, stats):
    """Render detailed view of a specific stage"""
    with st.expander(f"{stage['icon']} {stage['name']} ({stats['total']} applications)", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**Description:** {stage['description']}")
            
            if stage['ai_action']:
                st.markdown(f"🤖 **AI Agent Action:** {stage['ai_action']}")
            
            if stage['human_action']:
                st.markdown(f"👤 **Human Action Required:** {stage['human_action']}")
        
        with col2:
            st.metric("Total Applications", stats['total'])
            st.metric("Urgent Cases", stats['urgent'], delta=None if stats['urgent'] == 0 else f"{stats['urgent']} high priority")
            st.metric("Avg. Days in Process", f"{stats['avg_days']} days")
            if stats['overdue'] > 0:
                st.metric("Overdue (>30 days)", stats['overdue'], delta=f"-{stats['overdue']}", delta_color="inverse")
        
        # Show sample applications if any
        if stats['total'] > 0:
            st.markdown("---")
            st.markdown("**📋 Applications in this stage:**")
            
            # Display up to 5 sample applications
            for app in stats['applications'][:5]:
                cols = st.columns([2, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{app['application_number']}**")
                with cols[1]:
                    st.write(f"{app['days_in_process']} days")
                with cols[2]:
                    if app['urgent']:
                        st.write("🔴 Urgent")
                    else:
                        st.write("Standard")
                with cols[3]:
                    st.write(app['case_type'])
            
            if stats['total'] > 5:
                st.caption(f"... and {stats['total'] - 5} more applications")


def render_summary_metrics(applications, stage_stats):
    """Render summary metrics at the top"""
    st.markdown("### 📊 Overview Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_apps = len(applications)
    total_urgent = sum(1 for app in applications if app['urgent'])
    total_overdue = sum(1 for app in applications if app['days_in_process'] > 30)
    avg_processing_time = sum(app['days_in_process'] for app in applications) / total_apps if total_apps > 0 else 0
    
    # Calculate AI interventions needed
    ai_intervention_stages = ['ready_for_matching', 'verification', 'decision']
    ai_needed = sum(stage_stats[stage_id]['total'] for stage_id in ai_intervention_stages)
    
    with col1:
        st.metric("Total Applications", total_apps, help="All active applications in the system")
    
    with col2:
        st.metric("Urgent Cases", total_urgent, 
                  delta=f"{(total_urgent/total_apps*100):.1f}%" if total_apps > 0 else "0%",
                  help="High priority applications requiring immediate attention")
    
    with col3:
        st.metric("AI Processing", ai_needed,
                  help="Applications awaiting AI agent processing")
    
    with col4:
        st.metric("Overdue (>30 days)", total_overdue,
                  delta=None if total_overdue == 0 else f"-{total_overdue}",
                  delta_color="inverse",
                  help="Applications exceeding 30-day processing target")
    
    with col5:
        st.metric("Avg. Processing Time", f"{avg_processing_time:.1f} days",
                  help="Average days since submission across all applications")


def render_status_distribution(applications):
    """Render status distribution chart"""
    st.markdown("### 📈 Status Distribution")
    
    status_counts = Counter(app['status'] for app in applications)
    
    # Create chart data
    chart_data = []
    for stage in WORKFLOW_STAGES:
        count = sum(status_counts.get(status, 0) for status in stage['statuses'])
        if count > 0:
            chart_data.append({
                'Stage': stage['display'],
                'Count': count
            })
    
    if chart_data:
        import pandas as pd
        df = pd.DataFrame(chart_data)
        st.bar_chart(df.set_index('Stage'))
    else:
        st.info("No application data available")


def render_ai_activity_panel(stage_stats):
    """Render AI agent activity panel"""
    st.markdown("### 🤖 AI Agent Activity Monitor")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔍 Matching Agent**")
        matching_count = stage_stats['ready_for_matching']['total']
        if matching_count > 0:
            st.warning(f"⏳ {matching_count} applications awaiting biometric matching")
            st.caption("Action: EU-VIS database search and face recognition")
        else:
            st.success("✅ No applications pending")
    
    with col2:
        st.markdown("**🔬 Verification Agent**")
        verification_count = stage_stats['verification']['total']
        if verification_count > 0:
            st.warning(f"⏳ {verification_count} applications in verification")
            st.caption("Action: Document authenticity and consistency checks")
        else:
            st.success("✅ No applications pending")
    
    with col3:
        st.markdown("**⚖️ Decision Agent**")
        decision_count = stage_stats['decision']['total']
        if decision_count > 0:
            st.error(f"⏳ {decision_count} applications awaiting decision")
            st.caption("Action: Generate decision recommendations")
        else:
            st.success("✅ No applications pending")


def render_human_intervention_panel(stage_stats):
    """Render human intervention required panel"""
    st.markdown("### 👤 Human Intervention Required")
    
    intervention_needed = []
    
    # Check each stage for human actions
    for stage in WORKFLOW_STAGES:
        stats = stage_stats[stage['id']]
        if stats['total'] > 0 and stage['human_action']:
            intervention_needed.append({
                'stage': stage['name'],
                'icon': stage['icon'],
                'count': stats['total'],
                'urgent': stats['urgent'],
                'action': stage['human_action'],
                'color': stage['color']
            })
    
    if intervention_needed:
        for item in intervention_needed:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 2])
                
                with col1:
                    st.markdown(f"{item['icon']} **{item['stage']}**")
                    st.caption(item['action'])
                
                with col2:
                    st.metric("Total", item['count'])
                    if item['urgent'] > 0:
                        st.markdown(f"🔴 **{item['urgent']}** urgent")
                
                with col3:
                    if st.button(f"View {item['stage']}", key=f"view_{item['stage']}", use_container_width=True):
                        st.info(f"Navigate to the appropriate page to handle {item['stage']} applications")
                
                st.markdown("---")
    else:
        st.success("✅ No immediate human intervention required")


def overview_page():
    """Application Overview Page - Main Entry Point"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Page header
    st.title("📊 Application Overview Dashboard")
    st.markdown("Real-time view of application pipeline and AI agent activity")
    
    st.divider()
    
    # Load all applications
    with st.spinner("Loading application data..."):
        applications = get_all_applications()
    
    if not applications:
        st.warning("No applications found in the system.")
        st.info("👉 Go to **Visa Intake** to create new applications.")
        return
    
    # Calculate statistics
    stage_stats = get_stage_statistics(applications)
    
    # Render summary metrics
    render_summary_metrics(applications, stage_stats)
    
    st.divider()
    
    # Render visual pipeline
    render_pipeline_visual(stage_stats)
    
    st.divider()
    
    # Render AI activity monitor
    render_ai_activity_panel(stage_stats)
    
    st.divider()
    
    # Render human intervention panel
    render_human_intervention_panel(stage_stats)
    
    st.divider()
    
    # Render status distribution
    render_status_distribution(applications)
    
    st.divider()
    
    # Render detailed stage information
    st.markdown("### 📋 Detailed Stage Information")
    
    for stage in WORKFLOW_STAGES:
        stats = stage_stats[stage['id']]
        render_stage_details(stage, stats)
    
    # Help section
    st.divider()
    with st.expander("ℹ️ How to Use This Dashboard"):
        st.markdown("""
        ### Application Overview Dashboard Guide
        
        **Purpose:**
        - Monitor the entire application pipeline at a glance
        - Identify bottlenecks and urgent cases
        - Track AI agent workload
        - Plan human resource allocation
        
        **Key Sections:**
        
        1. **Overview Summary** - High-level metrics across all applications
        2. **Application Pipeline** - Visual flow showing applications at each stage
        3. **AI Agent Activity** - Monitor what AI agents are processing
        4. **Human Intervention** - See where human officers are needed
        5. **Status Distribution** - Chart showing application distribution
        6. **Detailed Stage Info** - Expandable details for each workflow stage
        
        **Workflow Stages:**
        
        📝 **New Application (Unassigned)** → New submissions awaiting assignment
        📋 **Intake Application** → Data entry and validation in progress  
        ✅ **Application Registered** → Successfully entered into system
        🔍 **Ready for Matching** → Awaiting EU-VIS biometric matching
        🔬 **To be Checked** → Document verification and fraud detection
        ⚖️ **To Decide** → Final decision stage (approve/reject)
        🖨️ **To Print** → Approved and ready for visa printing
        🎉 **Completed** → Fully processed and archived
        
        **Color Coding:**
        - 🔴 Red numbers = Urgent/overdue cases requiring immediate attention
        - 🟠 Orange = Warning states (rolled back, awaiting match)
        - 🟢 Green = Completed or on-track
        - 🔵 Blue = In progress
        
        **Action Items:**
        - Click "View" buttons to navigate to relevant pages
        - Expand stage details to see sample applications
        - Monitor AI activity to balance workload
        - Prioritize urgent cases (🔴 marked)
        """)
    
    # Refresh data button
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True, type="primary"):
            st.rerun()
