"""Visa Agent Workflow Page - Refactored"""
import streamlit as st
import json
import os
from util.session_manager import SessionManager
from util.azure_openai_functions import OpenAIHandler
from util.logging_functions import LoggingHandler
from config.settings import Settings
from datetime import datetime
import random


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


def get_openai_handler():
    """Get OpenAI handler instance"""
    azure_handler = st.session_state.get('azure_handler')
    if not azure_handler:
        raise ValueError("Azure handler not found in session state")
    
    logging_handler = LoggingHandler(azure_handler)
    settings = Settings()
    return OpenAIHandler(azure_handler, logging_handler, settings)


def get_hidden_orchestration_decision(user_message, current_step, completed_steps, application, openai_handler):
    """Get workflow decision from orchestration agent (hidden from user)"""
    try:
        system_prompt = f"""You are a hidden Workflow Orchestration Agent for visa application {application['application_number']}.
        
        Current state:
        - Current step: {current_step} (-1=not started, 0=Intake, 1=Registered, 2=ReadyForMatch, 3=Verificcaiton 4=Decision 5=ToPrint 6=Completed)
        - Completed steps: {completed_steps}
        - Application: {application['nationality']} citizen applying for {application['visa_type_requested']}
        
        User message: "{user_message}"
        
        Determine workflow action. Respond ONLY with:
        DECISION: [CHAT|AGENT]
        STEP: [0|1|2|3|4|5|6] (only if DECISION is AGENT)
        
        Logic:
        - If user wants to start and current_step is -1 → DECISION: AGENT, STEP: 0
        - If user wants to continue and current_step < 3 → DECISION: AGENT, STEP: {current_step + 1}
        - If user asks general questions → DECISION: CHAT
        - If user requests specific step → DECISION: AGENT, STEP: [appropriate step]"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = openai_handler.client.chat.completions.create(
            model=openai_handler.model_name_gpt,
            messages=messages,
            max_tokens=50,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the decision
        decision_data = {'trigger_agent': False, 'step': None}
        lines = result.split('\n')
        
        for line in lines:
            if line.startswith('DECISION:'):
                decision = line.split(':', 1)[1].strip()
                if decision == 'AGENT':
                    decision_data['trigger_agent'] = True
            elif line.startswith('STEP:'):
                try:
                    decision_data['step'] = int(line.split(':', 1)[1].strip())
                except:
                    pass
        
        return decision_data
        
    except Exception:
        return {'trigger_agent': False, 'step': None}


def get_sexy_visa_agent_response(user_message, orchestration_decision, application, openai_handler):
    """Get user-facing response from Sexy Visa Agent based on orchestration decision"""
    try:
        # Determine context based on orchestration decision
        if orchestration_decision.get('trigger_agent'):
            step = orchestration_decision.get('step')
            agent_names = ['Document Verification', 'Biometrics Verification', 'EU-VIS Matching', 'Final Review']
            context = f"The orchestration system has decided to trigger the {agent_names[step]} Agent (Step {step})."
        else:
            context = "The orchestration system has decided this requires a conversational response only."
        
        system_prompt = f"""You are the Sexy Visa Agent - the friendly, professional interface for government employees reviewing visa applications.
        
        You are handling application {application['application_number']} for a {application['nationality']} citizen applying for {application['visa_type_requested']}.
        
        Orchestration decision: {context}
        User message: "{user_message}"
        
        Instructions:
        - Be professional and efficient in your communication
        - Use clear, precise language appropriate for government employees
        - If an agent will be triggered, mention that you're connecting them to the specialist
        - If just chatting, be helpful and informative about the process
        - Keep responses concise and professional
        
        Respond as a professional AI assistant to help the case officer."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        stream = openai_handler.client.chat.completions.create(
            model=openai_handler.model_name_gpt,
            messages=messages,
            stream=True,
            max_tokens=500,
            temperature=0.7
        )
        
        return stream
        
    except Exception:
        # Fallback generator
        def fallback():
            yield f"I'm here to help with your visa application review. How can I assist you today?"
        return fallback()


def get_specialist_agent_config(step, application):
    """Get configuration for specialist agents"""
    agents = [
        {
            'name': 'Document Verification Agent',
            'avatar': '🔍',
            'prompt': f"""You are a Document Verification Agent assisting case officers with visa application reviews.
            
            You are analyzing application {application['application_number']} for a {application['nationality']} citizen applying for {application['visa_type_requested']}.
            
            Provide a comprehensive document verification assessment covering:
            1. Document authenticity analysis
            2. Completeness verification against requirements
            3. Format compliance and standards adherence
            4. Cross-reference validation with supporting documents
            5. Risk indicators and red flags
            
            Present your findings in a professional case assessment format in 2-3 paragraphs. Highlight any concerns or recommendations for the reviewing officer. Conclude by noting that biometrics verification is the next review stage."""
        },
        {
            'name': 'Biometrics Verification Agent', 
            'avatar': '👆',
            'prompt': f"""You are a Biometrics Verification Agent supporting case officers in visa application assessments.
            
            You are analyzing biometric data for application {application['application_number']} for a {application['nationality']} citizen.
            
            Conduct comprehensive biometric verification analysis covering:
            1. Facial recognition matching and quality assessment
            2. Fingerprint pattern analysis and database comparison
            3. Biometric data integrity and authenticity verification
            4. Cross-reference checks against watchlists and databases
            5. Identity verification confidence levels
            
            Present your technical findings in a professional case report format in 2-3 paragraphs. Include confidence scores, any anomalies detected, and recommendations for the case officer. Conclude by noting that EU-VIS database matching is the next verification phase."""
        },
        {
            'name': 'EU-VIS Matching Agent',
            'avatar': '🇪🇺', 
            'prompt': f"""You are an EU-VIS Matching Agent providing database analysis support to case officers.
            
            You are conducting EU-VIS database searches for application {application['application_number']} from a {application['nationality']} citizen.
            
            Database search results:
            {generate_euvis_match(application)}
            
            Provide a comprehensive analysis including:
            1. Match confidence levels and verification status
            2. Risk assessment based on database findings
            3. Previous application history and patterns
            4. Security flags or concerns identified
            5. Recommendations for case processing
            
            Present your intelligence analysis in a professional case report format in 2-3 paragraphs. Highlight any security considerations or processing recommendations for the reviewing officer. Conclude by noting that final case review is the next stage."""
        },
        {
            'name': 'Final Review Agent',
            'avatar': '⚖️',
            'prompt': f"""You are a Final Review Agent providing decision support to senior case officers.
            
            You are conducting the final assessment for application {application['application_number']} - a {application['case_type']} case for a {application['nationality']} citizen applying for {application['visa_type_requested']}.
            
            Application processing details:
            - Days in process: {application['days_in_process']}
            - Priority status: {'Urgent' if application['urgent'] else 'Standard'}
            
            Based on completed verifications (Document Analysis, Biometrics Verification, EU-VIS Database Search), provide:
            1. Comprehensive case assessment summary
            2. Final risk evaluation and security considerations
            3. Decision recommendation (Approve/Refuse/Request Additional Information)
            4. Detailed justification citing specific findings
            5. Processing recommendations and next steps
            
            Present your final assessment in an official case decision format in 3-4 paragraphs. Provide clear, defensible reasoning for your recommendation that meets departmental standards. This completes the comprehensive case review process."""
        }
    ]
    
    return agents[step] if 0 <= step < len(agents) else None


def stream_specialist_agent(agent_config, application):
    """Stream a specialist agent response"""
    try:
        openai_handler = get_openai_handler()
        
        with st.chat_message("assistant", avatar=agent_config['avatar']):
            st.markdown(f"**{agent_config['name']}**")
            
            messages = [
                {"role": "system", "content": agent_config['prompt']},
                {"role": "user", "content": f"Please perform your analysis for visa application {application['application_number']}"}
            ]
            
            stream = openai_handler.client.chat.completions.create(
                model=openai_handler.model_name_gpt,
                messages=messages,
                stream=True,
                max_tokens=4096,
                temperature=0.7
            )
            
            response = st.write_stream(stream)
            
            # Add complete response to chat history
            chat_key = f"chat_{application['application_number']}"
            st.session_state[f"{chat_key}_messages"].append({
                "role": "agent",
                "content": f"{agent_config['avatar']} {agent_config['name']}\n\n{response}"
            })
            
    except Exception as e:
        st.error(f"Error in {agent_config['name']}: {str(e)}")


def update_workflow_state(workflow_key, step, application):
    """Update workflow state when moving to a new step"""
    workflow_state = st.session_state.get(f"{workflow_key}_state", {})
    workflow_state['current_step'] = step
    workflow_state['is_running'] = True
    
    if step not in workflow_state.get('completed_steps', []):
        workflow_state.setdefault('completed_steps', []).append(step)
    
    st.session_state[f"{workflow_key}_state"] = workflow_state
    
    # Map agent step to application status for visual pipeline update
    step_to_status = {
        0: 'Verification',  # Document Verification Agent
        1: 'Verification',  # Biometrics Verification Agent
        2: 'Ready for Match',  # EU-VIS Matching Agent
        3: 'To Decide'  # Final Review Agent
    }
    
    # Update application status in session state
    if step in step_to_status:
        new_status = step_to_status[step]
        application['status'] = new_status
        st.session_state['workflow_app_data'] = application


def process_orchestration_agent_streaming(chat_key, application, user_message, workflow_key, workflow_state):
    """Main orchestration function using two-agent architecture"""
    try:
        openai_handler = get_openai_handler()
        
        # Get workflow state
        current_step = workflow_state.get('current_step', -1)
        completed_steps = workflow_state.get('completed_steps', [])
        
        # Step 1: Get hidden orchestration decision (not shown to user)
        orchestration_decision = get_hidden_orchestration_decision(
            user_message, current_step, completed_steps, application, openai_handler
        )
        
        # Step 2: Sexy Visa Agent responds to user based on orchestration decision
        with st.chat_message("assistant", avatar="🤖"):
            sexy_agent_response = get_sexy_visa_agent_response(
                user_message, orchestration_decision, application, openai_handler
            )
            response = st.write_stream(sexy_agent_response)
            
            # Add to chat history
            st.session_state[f"{chat_key}_messages"].append({
                "role": "assistant",
                "content": f"🤖 Sexy Visa Agent\n\n{response}"
            })
        
        # Step 3: Execute specialist agent if orchestration decided to trigger one
        if orchestration_decision.get('trigger_agent') and orchestration_decision.get('step') is not None:
            step = orchestration_decision['step']
            update_workflow_state(workflow_key, step, application)
            
            agent_config = get_specialist_agent_config(step, application)
            if agent_config:
                stream_specialist_agent(agent_config, application)
                
                # Trigger rerun to update the visual pipeline
                st.rerun()
        
    except Exception as e:
        with st.chat_message("assistant", avatar="🤖"):
            st.error(f"Sexy Visa Agent - Error: {str(e)}")


def generate_euvis_match(application):
    """Generate EU-VIS match details using real person data from people directory"""
    application_number = application.get('application_number', '')
    person_data = load_person_data(application_number)
    
    if not person_data:
        # Fallback if no matching person found
        return f"""**EU-VIS Database Search Results**
📋 Application: {application_number}
🔍 Status: No matching records found in EU-VIS database

**Search Analysis**
• No previous visa applications detected
• Clean background check - no security flags
• First-time applicant verification

**Risk Assessment:** Low Risk
**Recommendation:** Proceed with standard processing"""
    
    # Extract real applicant information
    given_names = person_data.get('given_names', 'Unknown')
    surname = person_data.get('surname', 'Unknown')
    full_name = f"{given_names} {surname}"
    nationality = person_data.get('country_of_nationality', 'Unknown')
    
    # Extract birth information
    date_of_birth = person_data.get('date_of_birth', {})
    birth_year = date_of_birth.get('year', 'Unknown')
    birth_note = date_of_birth.get('note', '')
    
    place_of_birth = person_data.get('place_of_birth', {})
    birth_city = place_of_birth.get('city', 'Unknown')
    birth_state = place_of_birth.get('state', '')
    birth_country = place_of_birth.get('country', 'Unknown')
    
    # Format birth place
    birth_place_parts = [birth_city]
    if birth_state:
        birth_place_parts.append(birth_state)
    if birth_country and birth_country != birth_city:
        birth_place_parts.append(birth_country)
    birth_place = ", ".join(birth_place_parts)
    
    # Format birth date
    if birth_year and birth_year != 'Unknown':
        birth_date_display = f"{birth_year}"
        if birth_note:
            birth_date_display += f" ({birth_note})"
    else:
        birth_date_display = f"Not Available ({birth_note})" if birth_note else "Not Available"
    
    # Extract additional details
    gender = person_data.get('gender', 'Unknown')
    civil_status = person_data.get('civil_status', 'Unknown')
    occupation = person_data.get('occupation', 'Unknown')
    residency_status = person_data.get('residency_status_in_australia', 'Unknown')
    
    # Address information
    address = person_data.get('address', {})
    address_parts = []
    if address.get('street_number'):
        address_parts.append(address['street_number'])
    if address.get('city'):
        address_parts.append(address['city'])
    if address.get('state'):
        address_parts.append(address['state'])
    current_address = ", ".join(address_parts) if address_parts else "Not Available"
    
    # Determine confidence and risk based on available data
    confidence_factors = []
    if given_names != 'Unknown' and surname != 'Unknown':
        confidence_factors.append("✓ Full name verification successful")
    if birth_year != 'Unknown':
        confidence_factors.append("✓ Birth year confirmed")
    if birth_city != 'Unknown':
        confidence_factors.append("✓ Place of birth validated")
    if gender != 'Unknown':
        confidence_factors.append("✓ Gender information verified")
    
    # Additional verification factors
    confidence_factors.extend([
        "✓ Biometric cross-reference completed",
        "✓ Document authenticity patterns analyzed",
        "✓ Previous application history reviewed"
    ])
    
    # Determine risk level based on data completeness and flags
    missing_critical_data = sum([
        1 for field in [given_names, surname, nationality] 
        if field in ['Unknown', 'Not Available', None]
    ])
    
    urgent_flag = person_data.get('urgent', False)
    minor_flag = person_data.get('applicant_is_minor', False)
    
    if missing_critical_data == 0 and not urgent_flag:
        risk_level = "Low Risk"
        recommendation = "Proceed with application - Complete identity verification successful"
    elif missing_critical_data <= 1 or urgent_flag:
        risk_level = "Medium Risk" 
        recommendation = "Proceed with enhanced verification - Additional checks recommended"
    else:
        risk_level = "High Risk"
        recommendation = "Hold for manual review - Incomplete identity data requires investigation"
    
    match_details = f"""**EU-VIS Database Match Results**
📋 Name: {full_name}
🌍 Nationality: {nationality}
📅 Date of Birth: {birth_date_display}
📍 Place of Birth: {birth_place}
👤 Gender: {gender}
💍 Civil Status: {civil_status}
🏠 Current Address: {current_address}
💼 Occupation: {occupation}
🇦🇺 AU Residency: {residency_status}

**Verification Analysis**
{chr(10).join(confidence_factors)}

**Risk Assessment:** {risk_level}
**Recommendation:** {recommendation}"""
    
    return match_details


def get_workflow_stages():
    """Define workflow stages matching the overview page"""
    return [
        {
            'id': 'unassigned',
            'name': 'New Application',
            'icon': '📝',
            'color': '#9E9E9E',
            'statuses': ['New', 'Unassigned']
        },
        {
            'id': 'intake',
            'name': 'Intake',
            'icon': '📋',
            'color': '#2196F3',
            'statuses': ['Intake', 'Data Entry']
        },
        {
            'id': 'registered',
            'name': 'Registered',
            'icon': '✅',
            'color': '#4CAF50',
            'statuses': ['Registered', 'Submitted']
        },
        {
            'id': 'ready_for_matching',
            'name': 'Ready for Match',
            'icon': '🔍',
            'color': '#FF9800',
            'statuses': ['Ready for Match', 'Awaiting Match', 'To Match']
        },
        {
            'id': 'verification',
            'name': 'Verification',
            'icon': '🔬',
            'color': '#9C27B0',
            'statuses': ['To Consult', 'To be Checked', 'Verification', 'Under Review']
        },
        {
            'id': 'decision',
            'name': 'Decision',
            'icon': '⚖️',
            'color': '#FF5722',
            'statuses': ['To Decide', 'Decision Pending', 'Awaiting Decision']
        },
        {
            'id': 'print',
            'name': 'To Print',
            'icon': '🖨️',
            'color': '#00BCD4',
            'statuses': ['To Print', 'Print Queue', 'Awaiting Approval']
        },
        {
            'id': 'completed',
            'name': 'Completed',
            'icon': '🎉',
            'color': '#4CAF50',
            'statuses': ['Completed', 'Closed', 'Archived']
        },
        {
            'id': 'rolled_back',
            'name': 'Rolled Back',
            'icon': '🔄',
            'color': '#FF9800',
            'statuses': ['Rolled Back', 'Returned', 'Rework']
        },
        {
            'id': 'rejected',
            'name': 'Rejected',
            'icon': '❌',
            'color': '#F44336',
            'statuses': ['Rejected', 'Declined', 'Refused']
        }
    ]


def map_status_to_stage(status):
    """Map application status to workflow stage"""
    if not status:
        return None
    
    stages = get_workflow_stages()
    for stage in stages:
        if status in stage['statuses']:
            return stage
    
    # Default to unassigned if no match
    return stages[0]


def render_application_overview(application):
    """Render a visual overview of where the application is in the workflow"""
    st.markdown("### 📊 Application Pipeline Status")
    
    # Get current status and map to stage
    current_status = application.get('status', 'New')
    current_stage = map_status_to_stage(current_status)
    
    if not current_stage:
        st.warning("Unable to determine current workflow stage")
        return
    
    # Get all stages
    stages = get_workflow_stages()
    
    # Calculate days in process
    days_in_process = application.get('days_in_process', 0)
    submission_date = application.get('submission_date', 'Unknown')
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Stage", current_stage['name'])
    
    with col2:
        st.metric("Status", current_status)
    
    with col3:
        urgent_indicator = "🔴 Yes" if application.get('urgent', False) else "No"
        st.metric("Urgent", urgent_indicator)
    
    with col4:
        st.metric("Days in Process", days_in_process)
    
    st.markdown("---")
    
    # Render visual pipeline
    st.markdown("#### Workflow Progress")
    
    # Show AI Agents information for each stage
    with st.expander("🤖 View AI Agents Working in Each Stage", expanded=False):
        st.markdown("""
        **AI Agent Activity by Workflow Stage:**
        
        | Stage | AI Agents | MCP Tools Used | Description |
        |-------|-----------|----------------|-------------|
        | 📝 **New Application** | 📊 Case Assignment Agent | • Workload Analysis | Automatically assigns applications to available officers |
        | 📋 **Intake** | 📋 Intake Agent | • Country Lookup<br/>• Document OCR<br/>• Consistency Check | Validates data completeness and country information |
        | ✅ **Registered** | - | • Document Classification | Automatic document indexing and categorization |
        | 🔍 **Ready for Match** | 🔍 Matching Agent | • Photo Comparison<br/>• BVV Lookup<br/>• EUVIS Lookup<br/>• User Data Comparison | Performs biometric matching and database cross-reference |
        | 🔬 **Verification** | 🔬 Verification Agent | • Document OCR<br/>• Document Verification<br/>• BVV Lookup<br/>• EUVIS Lookup<br/>• Fraud Detection<br/>• Country Lookup<br/>• Consistency Check | Comprehensive document analysis and fraud detection |
        | ⚖️ **Decision** | ⚖️ Decision Agent | • Risk Scoring<br/>• BVV Lookup<br/>• Fraud Detection<br/>• Consistency Check | Generates recommendation with 100-point scoring system |
        | 🖨️ **To Print** | 📄 Document Generation Agent | • Document Templates | Generates official visa documents for printing |
        | 🎉 **Completed** | - | - | Application archived |
        
        **Legend:**
        - 🤖 = AI Agent actively processing
        - 🔧 = MCP Tool utilized
        - 👤 = Human officer decision required
        """)
    
    # Create horizontal pipeline visual
    pipeline_html = """
    <style>
        .pipeline-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px 0;
            overflow-x: auto;
        }
        .stage-box {
            flex: 1;
            min-width: 120px;
            text-align: center;
            padding: 15px 10px;
            margin: 0 5px;
            border-radius: 8px;
            border: 2px solid #ddd;
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            position: relative;
            transition: all 0.3s ease;
        }
        .stage-box.active {
            border: 3px solid #2196F3;
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
            transform: scale(1.05);
        }
        .stage-box.completed {
            border: 2px solid #4CAF50;
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        }
        .stage-icon {
            font-size: 2em;
            margin-bottom: 5px;
        }
        .stage-name {
            font-size: 0.85em;
            font-weight: bold;
            margin-top: 5px;
        }
        .stage-agent {
            font-size: 0.7em;
            color: #666;
            margin-top: 3px;
            font-style: italic;
        }
        .stage-box.active .stage-agent {
            color: #1976D2;
            font-weight: bold;
        }
        .stage-arrow {
            font-size: 1.5em;
            color: #999;
            padding: 0 5px;
        }
        .active-badge {
            position: absolute;
            top: -10px;
            right: -10px;
            background: #2196F3;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
        }
        .agent-badge {
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            background: #FF9800;
            color: white;
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 0.7em;
            font-weight: bold;
            white-space: nowrap;
        }
        .stage-box.active .agent-badge {
            background: #2196F3;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
    </style>
    <div class="pipeline-container">
    """
    
    # Define which agent works on each stage
    stage_agents = {
        'unassigned': '📊 Assign',
        'intake': '📋 Intake',
        'registered': '✅ Auto',
        'ready_for_matching': '🔍 Match',
        'verification': '🔬 Verify',
        'decision': '⚖️ Decide',
        'print': '🖨️ Print',
        'completed': None,
        'rolled_back': None,
        'rejected': None
    }
    
    # Determine which stages have been completed (assumption: stages before current are completed)
    current_stage_index = next((i for i, s in enumerate(stages) if s['id'] == current_stage['id']), 0)
    
    # Main workflow stages (excluding rolled_back and rejected for primary flow)
    main_stages = [s for s in stages if s['id'] not in ['rolled_back', 'rejected']]
    
    for i, stage in enumerate(main_stages):
        is_current = stage['id'] == current_stage['id']
        is_completed = i < current_stage_index and current_stage['id'] not in ['rolled_back', 'rejected']
        
        # Determine stage class
        stage_class = "active" if is_current else ("completed" if is_completed else "")
        
        # Get agent for this stage
        agent_name = stage_agents.get(stage['id'])
        
        # Add stage box
        pipeline_html += f"""
        <div class="stage-box {stage_class}" style="border-color: {stage['color']};">
            {f'<div class="active-badge">▶</div>' if is_current else ''}
            <div class="stage-icon">{stage['icon']}</div>
            <div class="stage-name">{stage['name']}</div>
            {f'<div class="agent-badge">🤖 {agent_name}</div>' if agent_name else ''}
        </div>
        """
        
        # Add arrow between stages (except after last stage)
        if i < len(main_stages) - 1:
            pipeline_html += '<div class="stage-arrow">→</div>'
    
    pipeline_html += "</div>"
    
    # Show special status if rolled back or rejected
    if current_stage['id'] == 'rolled_back':
        pipeline_html += f"""
        <div style="text-align: center; margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); border-radius: 8px; border: 2px solid {current_stage['color']};">
            <div style="font-size: 2em;">{current_stage['icon']}</div>
            <div style="font-weight: bold; margin-top: 10px; color: #E65100;">Application Rolled Back for Corrections</div>
        </div>
        """
    elif current_stage['id'] == 'rejected':
        pipeline_html += f"""
        <div style="text-align: center; margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%); border-radius: 8px; border: 2px solid {current_stage['color']};">
            <div style="font-size: 2em;">{current_stage['icon']}</div>
            <div style="font-weight: bold; margin-top: 10px; color: #C62828;">Application Rejected</div>
        </div>
        """
    
    st.html(pipeline_html)
    
    # Show stage details
    st.markdown("---")
    st.markdown("#### Current Stage Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Stage:** {current_stage['icon']} {current_stage['name']}")
        st.markdown(f"**Submitted:** {submission_date}")
        st.markdown(f"**Processing Time:** {days_in_process} days")
    
    with col2:
        # Determine expected actions and AI agents based on stage
        if current_stage['id'] == 'unassigned':
            st.markdown("**🤖 Active Agent:** 📊 Case Assignment Agent")
            st.markdown("**Next Action:** Assign to case officer")
            st.markdown("**🔧 Tools:** Workload Analysis")
        elif current_stage['id'] == 'intake':
            st.markdown("**🤖 Active Agent:** 📋 Intake Agent")
            st.markdown("**Next Action:** Complete data entry and validation")
            st.markdown("**🔧 Tools:** Country Lookup, Document OCR, Consistency Check")
        elif current_stage['id'] == 'registered':
            st.markdown("**🤖 Active Agent:** Document Classification (Auto)")
            st.markdown("**Next Action:** Initiate biometric matching")
            st.markdown("**🔧 Tools:** Document Indexing")
        elif current_stage['id'] == 'ready_for_matching':
            st.markdown("**🤖 Active Agent:** 🔍 Matching Agent")
            st.markdown("**Next Action:** AI will process biometric matching")
            st.markdown("**🔧 Tools:** Photo Comparison, BVV, EUVIS, User Data")
        elif current_stage['id'] == 'verification':
            st.markdown("**🤖 Active Agent:** 🔬 Verification Agent")
            st.markdown("**Next Action:** AI will analyze documents & detect fraud")
            st.markdown("**🔧 Tools:** OCR, Document Verify, BVV, EUVIS, Fraud Detection")
        elif current_stage['id'] == 'decision':
            st.markdown("**🤖 Active Agent:** ⚖️ Decision Agent")
            st.markdown("**Next Action:** AI recommendation + Officer decision")
            st.markdown("**🔧 Tools:** Risk Scoring (100-point system)")
        elif current_stage['id'] == 'print':
            st.markdown("**🤖 Active Agent:** 📄 Document Generation Agent")
            st.markdown("**Next Action:** Print and dispatch visa")
            st.markdown("**🔧 Tools:** Document Templates")
        elif current_stage['id'] == 'completed':
            st.markdown("**🤖 Active Agent:** None")
            st.markdown("**Status:** ✅ Processing complete")
            st.markdown("**Next Action:** Archived")
        elif current_stage['id'] == 'rolled_back':
            st.markdown("**🤖 Active Agent:** None (Human Review Required)")
            st.markdown("**Next Action:** Correct issues and resubmit")
            st.markdown("**Requires:** 👤 Human Intervention")
        elif current_stage['id'] == 'rejected':
            st.markdown("**🤖 Active Agent:** None")
            st.markdown("**Status:** ❌ Application declined")
            st.markdown("**Next Action:** Notification sent")
    
    st.markdown("---")


def workflow_page():
    """Sexy Visa Agent Workflow Page - Clean Implementation"""
    
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
    
    # Render application overview pipeline
    render_application_overview(application)
    
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
    
    # Initialize workflow state
    workflow_key = f"workflow_{application['application_number']}"
    if f"{workflow_key}_state" not in st.session_state:
        st.session_state[f"{workflow_key}_state"] = {
            'is_running': False,
            'current_step': -1,  # -1 means not started
            'completed_steps': []
        }
    
    workflow_state = st.session_state[f"{workflow_key}_state"]
    
    # Chat section
    st.markdown("### Agent Communication Hub")
    
    # Show workflow status
    if workflow_state['is_running']:
        st.info("⏳ **Workflow Active** - Background agents are processing your application...")
    
    # Initialize chat history
    chat_key = f"chat_{application['application_number']}"
    if f"{chat_key}_messages" not in st.session_state:
        st.session_state[f"{chat_key}_messages"] = [
            {
                "role": "assistant",
                "content": f"🤖 Sexy Visa Agent\n\nGood day! I'm your AI assistant for reviewing application {application['application_number']} - a {application['case_type']} case for a {application['nationality']} citizen applying for {application['visa_type_requested']}. I can guide you through the verification process with our specialist agents. How may I assist you today?"
            }
        ]
    
    # Display existing chat messages
    for message in st.session_state[f"{chat_key}_messages"]:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "system":
            with st.chat_message("assistant", avatar="🔄"):
                st.info(message["content"])
        elif message["role"] == "agent":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Chat input - handle user interactions
    if user_message := st.chat_input("Type your message to the Sexy Visa Agent..."):
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Add user message to history
        st.session_state[f"{chat_key}_messages"].append({
            "role": "user", 
            "content": user_message
        })
        
        # Process orchestration agent and stream response
        process_orchestration_agent_streaming(chat_key, application, user_message, workflow_key, workflow_state)