"""Application Decision Page - AI-powered decision recommendations"""
import streamlit as st
import json
import os
from typing import Dict, Any
from util.session_manager import SessionManager
from util.azure_openai_functions import OpenAIHandler
from util.logging_functions import LoggingHandler
from services.decision_agent_service import DecisionAgentService
from config.settings import Settings
import asyncio


def load_person_data(application_number):
    """Load complete person data from people directory based on application number"""
    settings = Settings()
    people_dir = settings.PEOPLE_DIR
    
    if not os.path.exists(people_dir):
        return None
    
    for filename in os.listdir(people_dir):
        if filename.endswith('.json'):
            try:
                file_path = os.path.join(people_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('visa_application_number') == application_number:
                        return data
            except Exception:
                continue
    
    return None


def get_decision_service():
    """Get decision agent service instance"""
    azure_handler = st.session_state.get('azure_handler')
    if not azure_handler:
        raise ValueError("Azure handler not found in session state")
    
    logging_handler = LoggingHandler(azure_handler)
    settings = Settings()
    openai_handler = OpenAIHandler(azure_handler, logging_handler, settings)
    
    return DecisionAgentService(azure_handler, openai_handler)


def generate_mock_application_data(person_data: Dict[str, Any], application: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate mock application data for decision analysis
    This would normally come from verified document processing
    """
    import random
    
    # Mock financial data
    duration_days = random.randint(7, 45)
    accommodation_cost = random.uniform(500, 3000)
    bank_balance = random.uniform(2000, 15000)
    
    # Mock travel proof
    has_return_flight = random.choice([True, True, True, False])  # 75% have flights
    hotel_coverage = random.uniform(60, 100)
    
    # Mock background check
    police_statuses = ['clear', 'clear', 'clear', 'issues', 'missing']
    watchlist_statuses = ['clear', 'clear', 'clear', 'unknown']
    
    # Mock consistency checks
    name_consistent = random.choice([True, True, True, False])
    mrz_valid = random.choice([True, True, True, True, False])
    
    # Check for recent large inflows (flag if deposit within 14 days)
    recent_inflow = random.choice([True, False, False, False])
    inflow_days_ago = random.randint(1, 30) if recent_inflow else 0
    
    mock_data = {
        'application_number': application.get('application_number'),
        'given_name': person_data.get('given_names', ''),
        'surname': person_data.get('surname', ''),
        'country_of_nationality': person_data.get('country_of_nationality', ''),
        'visa_type_requested': application.get('visa_type_requested', ''),
        
        # Financial data
        'bank_balance': bank_balance,
        'duration_days': duration_days,
        'accommodation_cost': accommodation_cost,
        'destination_country': application.get('intake_location', 'Germany'),
        'recent_large_inflow': recent_inflow,
        'inflow_days_ago': inflow_days_ago,
        
        # Travel proof
        'has_return_flight': has_return_flight,
        'flight_dates_consistent': True if has_return_flight else False,
        'flight_names_match': name_consistent,
        'hotel_coverage_percentage': hotel_coverage,
        'hotel_refundable': random.choice([True, False]),
        
        # Background check
        'police_report_status': random.choice(police_statuses),
        'watchlist_status': random.choice(watchlist_statuses),
        'prior_violations': random.choice([False, False, False, True]),
        'entry_ban': random.choice([False, False, False, False, True]),  # Rare
        
        # Consistency
        'name_consistent_across_documents': name_consistent,
        'dates_consistent': random.choice([True, True, False]),
        'mrz_valid': mrz_valid,
        'document_integrity_score': random.uniform(85, 100),
        'photo_match_confidence': random.uniform(80, 100)
    }
    
    return mock_data


def display_score_gauge(score: int, max_score: int, label: str):
    """Display a visual score gauge"""
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    # Determine color
    if percentage >= 80:
        color = "#4CAF50"  # Green
    elif percentage >= 60:
        color = "#FF9800"  # Orange
    else:
        color = "#FF4444"  # Red
    
    html = f"""
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: 600; color: #333;">{label}</span>
            <span style="font-weight: 700; color: {color};">{score}/{max_score}</span>
        </div>
        <div style="
            width: 100%;
            height: 24px;
            background-color: #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            position: relative;
        ">
            <div style="
                width: {percentage}%;
                height: 100%;
                background-color: {color};
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                padding-right: 8px;
            ">
                <span style="color: white; font-size: 12px; font-weight: 600;">
                    {percentage:.0f}%
                </span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def display_decision_recommendation(recommendation: Dict[str, Any]):
    """Display the AI decision recommendation with visual elements"""
    decision = recommendation['decision_recommendation']
    
    # Status badge
    status = decision['status']
    status_colors = {
        'APPROVE': '#4CAF50',
        'REJECT': '#FF4444',
        'MANUAL_REVIEW': '#FF9800',
        'ERROR': '#9E9E9E'
    }
    
    status_icons = {
        'APPROVE': '✅',
        'REJECT': '❌',
        'MANUAL_REVIEW': '⚠️',
        'ERROR': '🔴'
    }
    
    color = status_colors.get(status, '#9E9E9E')
    icon = status_icons.get(status, '❓')
    
    st.markdown(f"""
    <div style="
        background-color: {color};
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="margin: 0; font-size: 32px;">{icon} {status.replace('_', ' ')}</h2>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Overall Score: {decision['score']}/100</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown("### 📊 Score Breakdown")
    
    breakdown = decision['score_breakdown']
    
    # Display gauges for each criterion
    display_score_gauge(
        breakdown['funds']['score'],
        breakdown['funds']['max_score'],
        "💰 Funds Sufficiency"
    )
    st.caption(breakdown['funds']['reason'])
    
    display_score_gauge(
        breakdown['travel_proof']['score'],
        breakdown['travel_proof']['max_score'],
        "✈️ Travel Proof Completeness"
    )
    st.caption(breakdown['travel_proof']['reason'])
    
    display_score_gauge(
        breakdown['background']['score'],
        breakdown['background']['max_score'],
        "🔍 Background Check"
    )
    st.caption(breakdown['background']['reason'])
    
    display_score_gauge(
        breakdown['consistency']['score'],
        breakdown['consistency']['max_score'],
        "📋 Document Consistency"
    )
    st.caption(breakdown['consistency']['reason'])
    
    st.divider()
    
    # Issues and concerns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚫 Blocking Issues")
        if decision['blocking_issues']:
            for issue in decision['blocking_issues']:
                st.error(f"• {issue}")
        else:
            st.success("No blocking issues detected")
    
    with col2:
        st.markdown("### ⚠️ Soft Concerns")
        if decision['soft_concerns']:
            for concern in decision['soft_concerns']:
                st.warning(f"• {concern}")
        else:
            st.info("No concerns identified")
    
    st.divider()
    
    # Policy references
    if decision['policy_refs']:
        st.markdown("### 📜 Policy References")
        st.caption(", ".join(decision['policy_refs']))
    
    # Justification
    st.markdown("### 📝 AI Justification")
    st.info(decision['justification'])


def decision_page():
    """Application Decision Page"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Get application data from session state
    if 'decision_app_data' not in st.session_state:
        st.warning("⚠️ No application selected for decision review.")
        st.info("👉 Please go to **Active Applications** (in the sidebar) and click the **🎯 Decide** button on an application.")
        return
    
    application = st.session_state['decision_app_data']
    
    # Page header
    st.title(f"🎯 Application Decision - {application['application_number']}")
    
    # Application summary
    with st.expander("📋 Application Summary", expanded=False):
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
    
    # Load person data
    person_data = load_person_data(application['application_number'])
    
    if not person_data:
        st.warning("Unable to load complete applicant data. Using application data only.")
        person_data = {}
    
    # Generate AI recommendation
    st.markdown("### 🤖 AI Decision Recommendation")
    
    # Button to generate recommendation
    if st.button("🔄 Generate AI Recommendation", type="primary", use_container_width=True):
        with st.spinner("Analyzing application data and generating recommendation..."):
            try:
                # Get decision service
                decision_service = get_decision_service()
                
                # Generate mock application data (in production, this would come from verified docs)
                application_data = generate_mock_application_data(person_data, application)
                
                # Generate recommendation
                recommendation = decision_service.generate_decision_recommendation(application_data)
                
                # Store in session state
                st.session_state['current_recommendation'] = recommendation
                st.session_state['current_application_data'] = application_data
                
                st.success("✅ AI recommendation generated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating recommendation: {str(e)}")
    
    # Display recommendation if available
    if 'current_recommendation' in st.session_state:
        recommendation = st.session_state['current_recommendation']
        application_data = st.session_state.get('current_application_data', {})
        
        display_decision_recommendation(recommendation)
        
        st.divider()
        
        # Get AI explanation
        st.markdown("### 💬 AI Expert Analysis")
        
        if st.button("🧠 Generate Detailed AI Analysis", use_container_width=True):
            with st.spinner("Generating expert analysis..."):
                try:
                    decision_service = get_decision_service()
                    
                    # Use asyncio to run async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    explanation = loop.run_until_complete(
                        decision_service.get_ai_recommendation_explanation(recommendation, application_data)
                    )
                    loop.close()
                    
                    st.session_state['ai_explanation'] = explanation
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating AI analysis: {str(e)}")
        
        # Display AI explanation if available
        if 'ai_explanation' in st.session_state:
            st.markdown(st.session_state['ai_explanation'])
        
        st.divider()
        
        # Human decision section
        st.markdown("### 👤 Human Officer Decision")
        st.info("⚠️ **Important:** The AI recommendation is advisory only. The final decision rests with the human officer.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            human_decision = st.selectbox(
                "Final Decision",
                options=["--- Select Decision ---", "APPROVE", "REJECT", "REQUEST MORE INFO"],
                key="human_decision"
            )
        
        with col2:
            officer_name = st.text_input("Officer Name", value=st.session_state.get('user', 'Unknown'))
        
        officer_notes = st.text_area(
            "Officer Notes & Justification",
            placeholder="Enter your decision rationale, noting any deviations from AI recommendation...",
            height=150
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Submit Decision", type="primary", use_container_width=True):
                if human_decision == "--- Select Decision ---":
                    st.error("Please select a final decision")
                elif not officer_notes:
                    st.error("Please provide officer notes and justification")
                else:
                    # Store decision (in production, save to database)
                    decision_record = {
                        'application_number': application['application_number'],
                        'ai_recommendation': recommendation['decision_recommendation']['status'],
                        'ai_score': recommendation['decision_recommendation']['score'],
                        'human_decision': human_decision,
                        'officer_name': officer_name,
                        'officer_notes': officer_notes,
                        'decided_at': st.session_state.get('current_timestamp', 'N/A')
                    }
                    
                    st.session_state['submitted_decision'] = decision_record
                    st.success(f"✅ Decision submitted: {human_decision}")
                    st.balloons()
        
        with col2:
            if st.button("📋 Save Draft", use_container_width=True):
                st.info("Draft saved (feature not yet implemented)")
        
        with col3:
            if st.button("🔙 Back to Applications", use_container_width=True):
                # Clear session state
                if 'current_recommendation' in st.session_state:
                    del st.session_state['current_recommendation']
                if 'ai_explanation' in st.session_state:
                    del st.session_state['ai_explanation']
                if 'decision_app_data' in st.session_state:
                    del st.session_state['decision_app_data']
                st.info("✅ Session cleared. Click 'Active Applications' in the sidebar to return.")
    
    else:
        st.info("👆 Click the button above to generate an AI recommendation for this application.")
    
    # Help section
    st.divider()
    with st.expander("ℹ️ Decision Criteria Information"):
        st.markdown("""
        ### Decision Scoring Criteria (100 points total)
        
        **💰 Funds Sufficiency (40 points)**
        - Evaluates bank balance against required funds
        - Considers destination daily costs and buffer requirements
        - Flags suspicious recent deposits
        
        **✈️ Travel Proof Completeness (20 points)**
        - Verifies return flight booking and date consistency
        - Assesses hotel coverage across stay duration
        - Checks name matching across documents
        
        **🔍 Background Check (20 points)**
        - Police clearance certificate status
        - Schengen database watchlist checks
        - Prior violations and entry bans
        
        **📋 Document Consistency (20 points)**
        - Cross-document name and date consistency
        - Passport MRZ validation
        - Document integrity and photo matching
        
        ### Decision Thresholds
        - **85+ points**: APPROVE recommendation
        - **60-84 points**: MANUAL_REVIEW recommendation
        - **Below 60**: REJECT recommendation
        - **Blocking issues**: Automatic MANUAL_REVIEW
        """)
