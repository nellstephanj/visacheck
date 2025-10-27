"""Case Assignment Orchestration Page

This page allows case managers to:
- View all available case workers (human and AI agents)
- See current workload distribution
- Assign cases intelligently using the orchestration agent
- View assignment recommendations
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from util.session_manager import SessionManager
from config.settings import Settings
from services.case_assignment_service import (
    get_orchestrator,
    AgentType,
    ExpertiseLevel
)


def load_pending_applications(people_dir, max_cases=50):
    """Load pending applications that need assignment"""
    files = list(Path(people_dir).glob("person_*.json"))[:max_cases]
    
    applications = []
    for file_path in files:
        with open(file_path, 'r') as f:
            person_data = json.load(f)
        
        # Calculate days in process
        submission_date_str = person_data.get('submission_date')
        if not submission_date_str:
            continue
        
        submission_date = datetime.strptime(submission_date_str, "%Y-%m-%d")
        days_in_process = (datetime.now() - submission_date).days
        
        application = {
            'application_number': person_data.get('visa_application_number', 'N/A'),
            'case_type': person_data.get('case_type', 'N/A'),
            'intake_location': person_data.get('intake_location', 'N/A'),
            'urgent': person_data.get('urgent', False),
            'days_in_process': days_in_process,
            'nationality': person_data.get('country_of_nationality', 'N/A'),
            'submission_date': submission_date.strftime("%d/%m/%Y")
        }
        applications.append(application)
    
    return applications


def render_agent_card(agent):
    """Render a card displaying agent information"""
    # Color based on agent type
    if agent.agent_type == AgentType.HUMAN:
        card_color = "#4CAF50"  # Green for human
        icon = "👤"
    else:
        card_color = "#2196F3"  # Blue for AI
        icon = "🤖"
    
    # Capacity bar color
    capacity_ratio = agent.get_capacity_ratio()
    if capacity_ratio < 0.5:
        capacity_color = "#4CAF50"
    elif capacity_ratio < 0.8:
        capacity_color = "#FF9800"
    else:
        capacity_color = "#F44336"
    
    # Render card
    st.markdown(f"""
    <div style="
        border: 2px solid {card_color};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: rgba(255, 255, 255, 0.05);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
            <span style="font-size: 18px; font-weight: bold;">{agent.name}</span>
        </div>
        <div style="margin-bottom: 8px;">
            <strong>ID:</strong> {agent.agent_id} | 
            <strong>Type:</strong> {agent.agent_type.value.upper()}
        </div>
        <div style="margin-bottom: 8px;">
            <strong>Workload:</strong> {agent.current_workload} / {agent.max_capacity}
        </div>
        <div style="
            width: 100%;
            height: 20px;
            background-color: #ddd;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        ">
            <div style="
                width: {capacity_ratio * 100}%;
                height: 100%;
                background-color: {capacity_color};
                transition: width 0.3s ease;
            "></div>
        </div>
        <div style="font-size: 12px; color: #888;">
            Capacity: {capacity_ratio:.1%}
        </div>
    </div>
    """, unsafe_allow_html=True)


def case_assignment_page():
    """Main case assignment orchestration page"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Page title
    st.title("🎯 Case Assignment Orchestration")
    st.markdown("Intelligent case assignment powered by AI orchestration")
    
    # Get orchestrator
    orchestrator = get_orchestrator()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "👥 Agent Pool",
        "📋 Assign Cases",
        "🔍 Recommendations"
    ])
    
    # TAB 1: DASHBOARD
    with tab1:
        st.header("Workload Overview")
        
        summary = orchestrator.get_workload_summary()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Agents", summary['total_agents'])
            st.caption(f"👤 {summary['human_agents']} Human | 🤖 {summary['ai_agents']} AI")
        
        with col2:
            st.metric("Available Agents", summary['available_agents'])
            st.caption("Can accept new cases")
        
        with col3:
            st.metric("Total Capacity", summary['total_capacity'])
            st.caption("Maximum case load")
        
        with col4:
            st.metric("Current Workload", summary['total_workload'])
            st.caption(f"{summary['overall_utilization']} utilized")
        
        st.divider()
        
        # Agent list with details
        st.subheader("Agent Status")
        
        # Separate human and AI agents
        human_agents = [a for a in orchestrator.agents if a.agent_type == AgentType.HUMAN]
        ai_agents = [a for a in orchestrator.agents if a.agent_type == AgentType.AI]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Human Agents")
            for agent in human_agents:
                render_agent_card(agent)
        
        with col2:
            st.markdown("### 🤖 AI Agents")
            for agent in ai_agents:
                render_agent_card(agent)
    
    # TAB 2: AGENT POOL
    with tab2:
        st.header("Agent Pool Details")
        
        # Filter options
        filter_type = st.selectbox(
            "Filter by Agent Type",
            ["All", "Human", "AI"],
            key="agent_filter"
        )
        
        # Get filtered agents
        if filter_type == "Human":
            filtered_agents = [a for a in orchestrator.agents if a.agent_type == AgentType.HUMAN]
        elif filter_type == "AI":
            filtered_agents = [a for a in orchestrator.agents if a.agent_type == AgentType.AI]
        else:
            filtered_agents = orchestrator.agents
        
        # Display detailed agent information
        for agent in filtered_agents:
            with st.expander(f"{agent.name} - {agent.agent_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Basic Information**")
                    st.write(f"**Type:** {agent.agent_type.value.upper()}")
                    st.write(f"**Max Capacity:** {agent.max_capacity}")
                    st.write(f"**Current Workload:** {agent.current_workload}")
                    st.write(f"**Available:** {'✅ Yes' if agent.is_available else '❌ No'}")
                    st.write(f"**Capacity Ratio:** {agent.get_capacity_ratio():.1%}")
                
                with col2:
                    st.markdown("**Case Type Expertise**")
                    for case_type, level in agent.case_type_expertise.items():
                        level_emoji = "⭐" * level.value
                        st.write(f"{level_emoji} {case_type}")
                    
                    st.markdown("**Location Expertise**")
                    for location, level in agent.location_expertise.items():
                        level_emoji = "⭐" * level.value
                        st.write(f"{level_emoji} {location}")
                
                # Show assigned cases if any
                if agent.assigned_cases:
                    st.markdown("**Currently Assigned Cases**")
                    for idx, case in enumerate(agent.assigned_cases[:5], 1):
                        st.write(f"{idx}. {case.get('application_number', 'N/A')} - {case.get('case_type', 'N/A')}")
                    
                    if len(agent.assigned_cases) > 5:
                        st.write(f"... and {len(agent.assigned_cases) - 5} more")
    
    # TAB 3: ASSIGN CASES
    with tab3:
        st.header("Batch Case Assignment")
        
        # Get pending applications
        settings = Settings()
        people_dir = settings.PEOPLE_DIR
        
        # Number of cases to load
        num_cases = st.slider("Number of cases to assign", 5, 100, 25)
        
        if st.button("🔄 Load Pending Cases", type="primary"):
            pending_cases = load_pending_applications(people_dir, num_cases)
            st.session_state['pending_cases'] = pending_cases
            st.success(f"✅ Loaded {len(pending_cases)} pending cases")
        
        if 'pending_cases' in st.session_state:
            pending_cases = st.session_state['pending_cases']
            
            st.write(f"**Pending Cases:** {len(pending_cases)}")
            
            # Options
            col1, col2 = st.columns(2)
            
            with col1:
                prioritize_urgent = st.checkbox("Prioritize Urgent Cases", value=True)
            
            with col2:
                if st.button("🎯 Assign All Cases", type="primary"):
                    # Reset workloads first for demo
                    orchestrator.reset_workloads()
                    
                    # Perform batch assignment
                    assignments = orchestrator.assign_cases_batch(
                        pending_cases,
                        prioritize_urgent=prioritize_urgent
                    )
                    
                    st.session_state['assignments'] = assignments
                    st.success("✅ Cases assigned successfully!")
                    st.rerun()
            
            # Display pending cases
            st.subheader("Pending Cases Preview")
            
            # Show first 10 cases
            for idx, case in enumerate(pending_cases[:10], 1):
                urgent_badge = "🔴 URGENT" if case['urgent'] else ""
                st.write(
                    f"{idx}. **{case['application_number']}** - "
                    f"{case['case_type']} | "
                    f"{case['intake_location']} | "
                    f"{case['days_in_process']} days {urgent_badge}"
                )
            
            if len(pending_cases) > 10:
                st.write(f"... and {len(pending_cases) - 10} more cases")
        
        # Display assignments if available
        if 'assignments' in st.session_state:
            st.divider()
            st.subheader("📊 Assignment Results")
            
            assignments = st.session_state['assignments']
            
            # Summary metrics
            total_assigned = sum(
                len(data['cases']) 
                for agent_id, data in assignments.items() 
                if agent_id != 'unassigned'
            )
            total_unassigned = len(assignments.get('unassigned', {}).get('cases', []))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Assigned", total_assigned)
            with col2:
                st.metric("Unassigned", total_unassigned)
            with col3:
                success_rate = (total_assigned / (total_assigned + total_unassigned) * 100) if (total_assigned + total_unassigned) > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            st.divider()
            
            # Show assignments per agent
            for agent_id, data in assignments.items():
                if agent_id == 'unassigned':
                    continue
                
                agent = data['agent']
                cases = data['cases']
                
                with st.expander(f"{agent.name} - {len(cases)} cases assigned"):
                    for case_data in cases:
                        case = case_data['case']
                        score = case_data['score']
                        
                        urgent_badge = "🔴" if case['urgent'] else ""
                        st.write(
                            f"• **{case['application_number']}** {urgent_badge} | "
                            f"Score: {score:.2f} | "
                            f"{case['case_type']} | "
                            f"{case['intake_location']}"
                        )
            
            # Show unassigned cases if any
            if 'unassigned' in assignments:
                with st.expander(f"⚠️ Unassigned Cases - {total_unassigned} cases", expanded=True):
                    st.warning("These cases could not be assigned due to capacity constraints")
                    for case_data in assignments['unassigned']['cases']:
                        case = case_data['case']
                        st.write(
                            f"• **{case['application_number']}** | "
                            f"{case['case_type']} | "
                            f"{case['intake_location']}"
                        )
    
    # TAB 4: RECOMMENDATIONS
    with tab4:
        st.header("🔍 Case Assignment Recommendations")
        st.write("Get intelligent recommendations for assigning specific cases")
        
        # Manual case input
        st.subheader("Enter Case Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            case_number = st.text_input("Application Number", "TEST-12345")
            case_type = st.selectbox(
                "Case Type",
                ["Schengen Short Stay", "Work Visa", "Student Visa"]
            )
            intake_location = st.selectbox(
                "Intake Location",
                ["Sydney FO", "Melbourne FO", "Brisbane FO"]
            )
        
        with col2:
            is_urgent = st.checkbox("Urgent Case")
            days_in_process = st.number_input("Days in Process", 0, 365, 5)
            nationality = st.text_input("Nationality", "Australian")
        
        if st.button("Get Recommendations", type="primary"):
            # Create case dictionary
            test_case = {
                'application_number': case_number,
                'case_type': case_type,
                'intake_location': intake_location,
                'urgent': is_urgent,
                'days_in_process': days_in_process,
                'nationality': nationality
            }
            
            # Get recommendations
            recommendations = orchestrator.recommend_assignment(test_case)
            
            if recommendations:
                st.success(f"✅ Found {len(recommendations)} agent recommendations")
                
                for idx, rec in enumerate(recommendations, 1):
                    agent = rec['agent']
                    score = rec['score']
                    reasoning = rec['reasoning']
                    
                    # Agent type badge
                    type_badge = "👤 HUMAN" if agent.agent_type == AgentType.HUMAN else "🤖 AI"
                    
                    with st.expander(f"#{idx} - {agent.name} (Score: {score:.2f})", expanded=(idx == 1)):
                        st.markdown(f"**{type_badge}**")
                        st.write(f"**Agent ID:** {agent.agent_id}")
                        st.write(f"**Current Workload:** {agent.current_workload} / {agent.max_capacity}")
                        st.write(f"**Capacity:** {agent.get_capacity_ratio():.1%}")
                        
                        st.markdown("**Why this agent?**")
                        for reason in reasoning:
                            st.write(f"• {reason}")
                        
                        # Expertise breakdown
                        expertise_score = agent.get_expertise_score(case_type, intake_location)
                        st.write(f"**Expertise Score:** {expertise_score:.1f} / 3.0")
                        
                        if idx == 1:
                            st.success("✨ **Recommended Best Match**")
            else:
                st.warning("⚠️ No available agents found. All agents are at capacity.")
    
    # Footer
    st.divider()
    st.markdown("### 💡 About Case Assignment Orchestration")
    st.info("""
    The Case Assignment Orchestration Agent intelligently distributes cases based on:
    
    - **Agent Expertise**: Matches cases to agents with relevant experience in case types and locations
    - **Workload Balancing**: Distributes cases evenly to prevent agent overload
    - **Processing Capacity**: AI agents can handle more cases than human agents
    - **Urgent Prioritization**: Urgent cases are prioritized and assigned to appropriate agents
    - **Human Verification**: Human agents are available to verify AI agent work
    
    This ensures optimal resource utilization and faster case processing times.
    """)
    
    # Help section
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button(
            "✉️ Contact Support",
            "mailto:support@visacheck.com",
            type="secondary",
            use_container_width=True
        )
    
    with col2:
        st.link_button(
            "📚 Documentation",
            "https://example.com/case-assignment-docs",
            type="secondary",
            use_container_width=True
        )
