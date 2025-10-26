"""Visa Agent Workflow Page"""
import streamlit as st
import json
from datetime import datetime
from util.session_manager import SessionManager
from util.azure_openai_functions import OpenAIHandler
from util.azure_functions import AzureHandler
from util.logging_functions import LoggingHandler
from config.settings import Settings
import random


def get_openai_handler():
    """Get OpenAI handler instance"""
    azure_handler = st.session_state.get('azure_handler')
    if not azure_handler:
        raise ValueError("Azure handler not found in session state")
    
    logging_handler = LoggingHandler(azure_handler)
    settings = Settings()
    return OpenAIHandler(azure_handler, logging_handler, settings)


def process_orchestration_agent(chat_key, application, user_message):
    """Orchestration agent that uses LLM to parse current step and user intent"""
    try:
        openai_handler = get_openai_handler()
        workflow_key = f"workflow_{application['application_number']}"
        workflow_state = st.session_state.get(f"{workflow_key}_state", {
            'is_running': False,
            'current_step': -1,  # -1 means not started, 0-3 are the steps
            'completed_steps': []
        })
        
        # Create system prompt for orchestration agent
        system_prompt = f"""You are an Orchestration Agent managing a visa application workflow. Your job is to:
1. Parse the current workflow state
2. Understand user intent from their message
3. Decide what action to take
4. Respond appropriately and indicate if a specialist agent should be called

CURRENT WORKFLOW STATE:
- Application: {application['application_number']} ({application['nationality']} citizen, {application['visa_type_requested']})
- Current Step: {workflow_state['current_step']} (-1=not started, 0=documents, 1=biometrics, 2=euvis, 3=final)
- Completed Steps: {workflow_state.get('completed_steps', [])}
- Is Running: {workflow_state['is_running']}

WORKFLOW STEPS:
0. Document Verification Agent - Reviews document authenticity and completeness
1. Biometrics Verification Agent - Analyzes fingerprints and facial recognition
2. EU-VIS Matching Agent - Performs database matching and cross-references
3. Final Review Agent - Makes final decision and recommendations

RESPONSE FORMAT:
You must respond with a JSON object containing:
{{
    "response_text": "Your conversational response to the user",
    "action": "start|next|jump|status|chat|complete",
    "target_step": number (0-3, only if action requires it),
    "call_agent": true/false,
    "reasoning": "Brief explanation of your decision"
}}

ACTIONS:
- "start": Begin the workflow (step 0)
- "next": Move to next step in sequence  
- "jump": Jump to specific step
- "status": Provide current status info
- "chat": General conversation
- "complete": Workflow is finished

GUIDELINES:
- If current_step is -1 and user wants to start: action="start", target_step=0, call_agent=true
- If user says "yes"/"continue"/"next" and current step < 3: action="next", target_step=current_step+1, call_agent=true
- If user asks about specific step: action="jump", target_step=X, call_agent=true
- If user asks for status/progress: action="status", call_agent=false
- If general chat: action="chat", call_agent=false
- If current_step=3 and user confirms: action="complete", call_agent=false

Be conversational and helpful while being precise about workflow management.

User message: "{user_message}"

Respond with the JSON object:"""

        # Get orchestration response
        chat_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response_content = ""
        for chunk in openai_handler.chat_with_gpt(chat_history):
            response_content += chunk
        
        # Parse the JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            json_str = response_content[start_idx:end_idx]
            orchestration_result = json.loads(json_str)
            
            # Add orchestration agent message
            st.session_state[f"{chat_key}_messages"].append({
                "role": "agent",
                "content": f"🤖 Coordination Agent\n\n{orchestration_result['response_text']}"
            })
            
            # Execute the action if needed
            if orchestration_result.get('call_agent', False):
                execute_workflow_action(orchestration_result, chat_key, application, workflow_key, workflow_state)
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            st.session_state[f"{chat_key}_messages"].append({
                "role": "agent",
                "content": f"🤖 Coordination Agent\n\n{response_content}"
            })
        
        return True
        
    except Exception as e:
        add_agent_message(chat_key, "🤖 Coordination Agent", f"Error in orchestration: {str(e)}")
        return False


def execute_workflow_action(orchestration_result, chat_key, application, workflow_key, workflow_state):
    """Execute the action determined by the orchestration agent"""
    action = orchestration_result.get('action')
    target_step = orchestration_result.get('target_step')
    
    if action in ['start', 'next', 'jump']:
        # Update workflow state
        workflow_state['is_running'] = True
        workflow_state['current_step'] = target_step
        
        if target_step not in workflow_state.get('completed_steps', []):
            workflow_state.setdefault('completed_steps', []).append(target_step)
        
        st.session_state[f"{workflow_key}_state"] = workflow_state
        
        # Call the appropriate agent
        if target_step == 0:
            process_document_agent(chat_key, application)
        elif target_step == 1:
            process_biometrics_agent(chat_key, application)
        elif target_step == 2:
            process_euvis_agent(chat_key, application)
        elif target_step == 3:
            process_final_review_agent(chat_key, application)
            
    elif action == 'complete':
        workflow_state['is_running'] = False
        workflow_state['current_step'] = 4  # Beyond last step
        st.session_state[f"{workflow_key}_state"] = workflow_state


def process_orchestration_agent_streaming(chat_key, application, user_message, workflow_key, workflow_state):
    """Modern orchestration agent with proper streaming"""
    try:
        openai_handler = get_openai_handler()
        
        # Get workflow state
        current_step = workflow_state.get('current_step', -1)
        completed_steps = workflow_state.get('completed_steps', [])
        
        # Step 1: Get hidden orchestration decision (not shown to user)
        orchestration_decision = get_hidden_orchestration_decision(user_message, current_step, completed_steps, application, openai_handler)
        
        # Step 2: Sexy Visa Agent responds to user based on orchestration decision
        with st.chat_message("assistant", avatar="💎"):
            sexy_agent_response = get_sexy_visa_agent_response(user_message, orchestration_decision, application, openai_handler)
            response = st.write_stream(sexy_agent_response)
            
            # Add to chat history
            st.session_state[f"{chat_key}_messages"].append({
                "role": "assistant",
                "content": f"💎 Sexy Visa Agent\n\n{response}"
            })
        
        # Step 3: Execute specialist agent if orchestration decided to trigger one
        if orchestration_decision.get('trigger_agent') and orchestration_decision.get('step') is not None:
            agent_info = {'step': orchestration_decision['step'], 'name': ['Document Verification', 'Biometrics Verification', 'EU-VIS Matching', 'Final Review'][orchestration_decision['step']]}
            call_specialist_agent_streaming(agent_info, application, workflow_key, workflow_state)
        
    except Exception as e:
        with st.chat_message("assistant", avatar="🎯"):
            st.error(f"Workflow Orchestration Agent - Error: {str(e)}")


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
        
    except Exception as e:
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
        - Be professional but friendly and engaging
        - Use clear, helpful language appropriate for government employees
        - If an agent will be triggered, mention that you're connecting them to the specialist
        - If just chatting, be helpful and informative about the process
        - Keep responses concise but warm
        - Use the 💎 personality - professional but with a touch of elegance
        
        Respond as the Sexy Visa Agent would to help the case officer."""
        
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
        
    except Exception as e:
        # Fallback generator
        def fallback():
            yield f"I'm here to help with your visa application review. How can I assist you today?"
        return fallback()


def parse_orchestration_response(response, chat_key, application, workflow_key, workflow_state):
    """Parse the orchestration agent's structured response and take appropriate action"""
    try:
        lines = response.strip().split('\n')
        decision = None
        step = None
        response_text = ""
        
        # Parse the structured response
        for line in lines:
            if line.startswith('DECISION:'):
                decision = line.split(':', 1)[1].strip()
            elif line.startswith('STEP:'):
                step = int(line.split(':', 1)[1].strip())
            elif line.startswith('RESPONSE:'):
                response_text = line.split(':', 1)[1].strip()
        
        # Only show the human-readable response to the user
        if response_text:
            st.session_state[f"{chat_key}_messages"].append({
                "role": "assistant",
                "content": f"🎯 Workflow Orchestration Agent\n\n{response_text}"
            })
        
        # If decision is to trigger an agent, do so silently
        if decision == 'AGENT' and step is not None:
            agent_info = {'step': step, 'name': ['Document Verification', 'Biometrics Verification', 'EU-VIS Matching', 'Final Review'][step]}
            call_specialist_agent_streaming(agent_info, application, workflow_key, workflow_state)
            
    except Exception as e:
        # Fallback: treat entire response as human-readable (for when LLM doesn't follow format)
        st.session_state[f"{chat_key}_messages"].append({
            "role": "assistant",
            "content": f"🎯 Workflow Orchestration Agent\n\n{response}"
        })


def call_specialist_agent_streaming(agent_info, application, workflow_key, workflow_state):
    """Call the appropriate specialist agent with streaming"""
    step = agent_info['step']
    
    # Update workflow state
    workflow_state['current_step'] = step
    workflow_state['is_running'] = True
    if step not in workflow_state.get('completed_steps', []):
        workflow_state.setdefault('completed_steps', []).append(step)
    st.session_state[f"{workflow_key}_state"] = workflow_state
    
    # Agent configurations
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
    
    if 0 <= step < len(agents):
        agent = agents[step]
        stream_specialist_agent(agent, application)


def stream_specialist_agent(agent, application):
    """Stream a specialist agent response"""
    try:
        openai_handler = get_openai_handler()
        
        with st.chat_message("assistant", avatar=agent['avatar']):
            st.markdown(f"**{agent['name']}**")
            
            # Prepare messages
            messages = [
                {"role": "system", "content": agent['prompt']},
                {"role": "user", "content": f"Please perform your analysis for visa application {application['application_number']}"}
            ]
            
            # Create OpenAI stream
            stream = openai_handler.client.chat.completions.create(
                model=openai_handler.model_name_gpt,
                messages=messages,
                stream=True,
                max_tokens=4096,
                temperature=0.7
            )
            
            # Stream the response
            response = st.write_stream(stream)
            
            # No need for specific follow-up instructions since orchestration agent handles conversation flow naturally
            
            # Add complete response to chat history
            chat_key = f"chat_{application['application_number']}"
            st.session_state[f"{chat_key}_messages"].append({
                "role": "agent",
                "content": f"{agent['avatar']} {agent['name']}\n\n{response}"
            })
            
    except Exception as e:
        st.error(f"Error in {agent['name']}: {str(e)}")




def generate_agent_response(user_message, application):
    """Generate contextual responses from the Sexy Visa Agent"""
    user_lower = user_message.lower()
    
    # Application-specific responses
    app_num = application['application_number']
    nationality = application['nationality']
    case_type = application['case_type']
    days = application['days_in_process']
    
    # Context-aware responses
    if any(word in user_lower for word in ['status', 'progress', 'update']):
        return f"Your application {app_num} has been in process for {days} days. Current status is 'To Decide'. Everything looks good so far! 📊"
    
    elif any(word in user_lower for word in ['document', 'docs', 'paperwork']):
        return f"For {case_type} applications from {nationality}, I can help verify your documents. What specific documents do you need assistance with? 📄"
    
    elif any(word in user_lower for word in ['biometric', 'fingerprint', 'photo']):
        return f"Biometric verification is required for your {case_type} application. Have you completed your biometric appointment? 👆"
    
    elif any(word in user_lower for word in ['urgent', 'expedite', 'rush']):
        urgent_status = "already marked as urgent" if application['urgent'] else "not currently marked as urgent"
        return f"Your application is {urgent_status}. I can help expedite processing if needed. Would you like me to review priority options? 🚨"
    
    elif any(word in user_lower for word in ['timeline', 'time', 'when', 'how long']):
        return f"Based on current processing times for {case_type} from {nationality}, typical processing takes 15-30 days. Your application at {days} days is {'on track' if days <= 20 else 'taking a bit longer than usual'}. ⏰"
    
    elif any(word in user_lower for word in ['problem', 'issue', 'error', 'wrong']):
        return f"I'm here to help resolve any issues with application {app_num}. Can you describe the specific problem you're experiencing? I'll do my best to assist! 🔧"
    
    elif any(word in user_lower for word in ['thank', 'thanks']):
        return random.choice([
            "You're very welcome! I'm here to make your visa process as smooth as possible! 😊",
            "My pleasure! Feel free to ask if you need anything else about your application! ✨",
            "Happy to help! That's what Sexy Visa Agents are for! 🤖💫"
        ])
    
    elif any(word in user_lower for word in ['hello', 'hi', 'hey']):
        return f"Hello there! Great to hear from you regarding application {app_num}. How can I assist you today? 👋"
    
    elif any(word in user_lower for word in ['help', 'assist']):
        return f"I can help you with:\n• Application status updates\n• Document verification\n• Processing timelines\n• Biometric appointments\n• General visa questions\n\nWhat would you like to know about application {app_num}? 🤝"
    
    else:
        # Generic helpful responses
        responses = [
            f"That's an interesting question about your {case_type} application! Let me see how I can help you with that. 🤔",
            f"Thanks for reaching out! I'm analyzing your request for application {app_num}. Can you provide a bit more detail? 🔍",
            f"I'm here to assist with your {nationality} visa application. Could you clarify what specific information you need? 💭",
            f"Great question! For application {app_num}, I want to make sure I give you the most accurate information. What specifically would you like to know? 🎯"
        ]
        return random.choice(responses)


def add_agent_message(chat_key, agent_name, message):
    """Add an agent message to the chat"""
    if f"{chat_key}_messages" not in st.session_state:
        st.session_state[f"{chat_key}_messages"] = []
    
    st.session_state[f"{chat_key}_messages"].append({
        "role": "agent",
        "content": f"{agent_name}\n\n{message}"
    })


def generate_euvis_match(application):
    """Generate realistic EU-VIS match details"""
    # Sample names for different nationalities
    sample_names = {
        "Australia": ["James Wilson", "Sarah Chen", "Michael Brown"],
        "Algeria": ["Youssef Naceur", "Amina Kader", "Omar Benali"], 
        "Morocco": ["Hassan Alami", "Fatima Zahra", "Ahmed Benjelloun"],
        "Tunisia": ["Karim Sassi", "Leila Trabelsi", "Mohamed Gharbi"],
        "Egypt": ["Ahmed Hassan", "Nour El-Din", "Yasmin Farouk"]
    }
    
    nationality = application.get('nationality', 'Unknown')
    names = sample_names.get(nationality, ["Unknown Person"])
    selected_name = random.choice(names)
    
    # Generate realistic birth date (between 1960-1995)
    birth_year = random.randint(1960, 1995)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    
    # Generate birth place based on nationality
    birth_places = {
        "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "Algeria": ["Algiers", "Oran", "Constantine", "Batna"],
        "Morocco": ["Casablanca", "Rabat", "Fez", "Marrakech"],
        "Tunisia": ["Tunis", "Sfax", "Sousse", "Kairouan"],
        "Egypt": ["Cairo", "Alexandria", "Giza", "Luxor"]
    }
    
    birth_place = random.choice(birth_places.get(nationality, ["Unknown"]))
    
    match_details = f"""**Match Details**
📋 Name: {selected_name}
🌍 Nationality: {nationality}
📅 Date of Birth: {birth_day:02d}/{birth_month:02d}/{birth_year}
📍 Place of Birth: {birth_place}

**Reasoning**
✓ Biometric similarity - Facial recognition shows high confidence match
✓ Document patterns - Similar document history patterns detected  
✓ Travel history - Overlapping travel destinations and dates

**Risk Assessment:** Low Risk
**Recommendation:** Proceed with application"""
    
    return match_details


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
                "content": f"💎 Sexy Visa Agent\n\nHello! I'm here to help you review application {application['application_number']} - a {application['case_type']} case for a {application['nationality']} citizen applying for {application['visa_type_requested']}. I can guide you through the verification process with our specialist agents. How can I assist you today?"
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
    
    # Chat input - this is the key change: handle everything in one block
    if user_message := st.chat_input("Type your message to the coordination agent..."):
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