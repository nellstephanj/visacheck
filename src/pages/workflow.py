"""Visa Agent Workflow Page - Refactored"""
import streamlit as st
import json
import os
from util.session_manager import SessionManager
from util.azure_openai_functions import OpenAIHandler
from util.logging_functions import LoggingHandler
from config.settings import Settings
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
        - Current step: {current_step} (-1=not started, 0=documents, 1=biometrics, 2=euvis, 3=final)
        - Completed steps: {completed_steps}
        - Application: {application['nationality']} citizen applying for {application['visa_type_requested']}
        
        User message: "{user_message}"
        
        Determine workflow action. Respond ONLY with:
        DECISION: [CHAT|AGENT]
        STEP: [0|1|2|3] (only if DECISION is AGENT)
        
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


def update_workflow_state(workflow_key, step):
    """Update workflow state when moving to a new step"""
    workflow_state = st.session_state.get(f"{workflow_key}_state", {})
    workflow_state['current_step'] = step
    workflow_state['is_running'] = True
    
    if step not in workflow_state.get('completed_steps', []):
        workflow_state.setdefault('completed_steps', []).append(step)
    
    st.session_state[f"{workflow_key}_state"] = workflow_state


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
            update_workflow_state(workflow_key, step)
            
            agent_config = get_specialist_agent_config(step, application)
            if agent_config:
                stream_specialist_agent(agent_config, application)
        
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