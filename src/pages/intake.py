"""Visa Application Intake Page"""
import streamlit as st
from datetime import datetime
from services.visa_application_service import VisaApplicationService
from util.session_manager import SessionManager


def intake_page():
    """Visa Application Intake Form"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Get handlers from session state
    azure_handler = st.session_state.get('azure_handler')
    
    if not azure_handler:
        st.error("Application initialization error. Please refresh the page.")
        return
    
    # Initialize service
    visa_service = VisaApplicationService(azure_handler)
    
    # Page title
    st.title("Visa Application Intake")
    
    # Verify with Agent button
    col1, col2 = st.columns([1, 5])
    with col1:
        verify_button = st.button("🔍 Verify with Agent", type="secondary", use_container_width=True)
    
    # Show modal dialog when verify button is clicked
    if verify_button:
        # Use experimental dialog for modal
        @st.dialog("⚠️ Intake Issue Detected", width="large")
        def show_verification_issues():
            # Custom CSS for red border and styling
            st.markdown("""
                <style>
                .stDialog > div:first-child {
                    border: 3px solid #FF4B4B !important;
                    border-radius: 8px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.error("**Issues found that require attention:**")
            st.write("")
            st.write("**1.** Special character **&** detected in name that might cause issue with BVV process")
            st.write("")
            st.write("**2.** The date of birth is missing")
            st.write("")
            
            if st.button("Close", use_container_width=True):
                st.rerun()
        
        show_verification_issues()
    
    st.divider()
    
    # Initialize session state for form data
    if 'intake_form_data' not in st.session_state:
        st.session_state['intake_form_data'] = {}
    
    # Create form
    with st.form("visa_intake_form"):
        
        # Application Number Section
        st.subheader("📋 Application Number")
        with st.container(border=True):
            application_number = st.text_input(
                "Visa Application Number",
                help="Enter the visa application number",
                placeholder="e.g., APP-2023-001"
            )
        
        st.divider()
        
        # Application Details Section
        st.subheader("📝 Application")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                case_type = st.selectbox(
                    "Case Type *",
                    options=[
                        "Schengen Short Stay",
                        "Long Stay",
                        "Transit",
                        "Other"
                    ],
                    help="Select the case type"
                )
            
            with col2:
                application_type = st.selectbox(
                    "Application Type *",
                    options=[
                        "Initial",
                        "MVV",
                        "Renewal",
                        "Extension"
                    ],
                    help="Select the application type"
                )
            
            with col3:
                intake_location = st.selectbox(
                    "Intake Location *",
                    options=[
                        "Sydney FO",
                        "Melbourne FO",
                        "Brisbane FO",
                        "Perth FO",
                        "Adelaide FO"
                    ],
                    help="Select the intake location"
                )
            
            col4, col5, col6 = st.columns(3)
            
            with col4:
                visa_type_requested = st.selectbox(
                    "Visa Type Requested *",
                    options=[
                        "Short Stay",
                        "Long Stay",
                        "Transit",
                        "Business",
                        "Tourist",
                        "Family Visit",
                        "Other"
                    ],
                    help="Select the visa type"
                )
            
            with col5:
                submission_date = st.date_input(
                    "Submission Date *",
                    value=datetime.now(),
                    help="Select the submission date"
                )
            
            with col6:
                applicant_is_minor = st.selectbox(
                    "Applicant is Minor? *",
                    options=["No", "Yes"],
                    help="Is the applicant a minor?"
                )
            
            col7, col8 = st.columns([1, 2])
            
            with col7:
                urgent = st.selectbox(
                    "Urgent",
                    options=["No", "Yes"],
                    help="Is this application urgent?"
                )
        
        st.divider()
        
        # Applicant Details Section
        st.subheader("👤 Applicant")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            
            with col1:
                given_name = st.text_input(
                    "Given Name(s) *",
                    help="Enter the given name(s)",
                    placeholder="e.g., Ellie"
                )
            
            with col2:
                surname = st.text_input(
                    "Surname / Family Name(s) *",
                    help="Enter the surname",
                    placeholder="e.g., Pearce"
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                surname_at_birth = st.text_input(
                    "Surname at Birth *",
                    help="Enter the surname at birth",
                    placeholder="e.g., Walsh"
                )
            
            with col4:
                variation_in_birth_certificate = st.selectbox(
                    "Variation in Birth Certificate?",
                    options=["No", "Yes"],
                    help="Any variation in birth certificate?"
                )
            
            col5, col6, col7 = st.columns(3)
            
            with col5:
                gender = st.selectbox(
                    "Gender / Sex *",
                    options=["Female", "Male", "Other", "Prefer not to say"],
                    help="Select gender"
                )
            
            with col6:
                current_nationality = st.selectbox(
                    "Current Nationality *",
                    options=[
                        "Australian",
                        "New Zealand",
                        "British",
                        "American",
                        "Canadian",
                        "Other"
                    ],
                    help="Select current nationality"
                )
            
            with col7:
                country_of_nationality = st.text_input(
                    "Country of Nationality *",
                    value="Australia",
                    help="Enter country of nationality"
                )
        
        st.divider()
        
        # Address Section
        st.subheader("🏠 Address")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            
            with col1:
                street = st.text_input(
                    "Street *",
                    help="Enter street name",
                    placeholder="e.g., Eugella Road"
                )
            
            with col2:
                house_number = st.text_input(
                    "House Number",
                    help="Enter house number",
                    placeholder="e.g., 11"
                )
            
            col3, col4 = st.columns(2)
            
            with col3:
                unit_number = st.text_input(
                    "Unit Number / Lot# / Suffix",
                    help="Enter unit number or suffix",
                    placeholder="e.g., A"
                )
            
            with col4:
                postal_code = st.text_input(
                    "Postal Code *",
                    help="Enter postal code",
                    placeholder="e.g., 4802"
                )
            
            col5, col6 = st.columns(2)
            
            with col5:
                city = st.text_input(
                    "City *",
                    help="Enter city",
                    placeholder="e.g., Mount Rooper"
                )
            
            with col6:
                country = st.selectbox(
                    "Country *",
                    options=[
                        "Australia",
                        "New Zealand",
                        "United Kingdom",
                        "United States",
                        "Canada",
                        "Other"
                    ],
                    help="Select country"
                )
        
        st.divider()
        
        # Birth Information Section
        st.subheader("🎂 Birth Information")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date_of_birth_indicator = st.selectbox(
                    "Date of Birth Indicator *",
                    options=[
                        "Complete: Day, month and year",
                        "Incomplete: Only year",
                        "Incomplete: Month and year"
                    ],
                    help="Select the level of date of birth information available"
                )
            
            with col2:
                if "Complete" in date_of_birth_indicator:
                    date_of_birth = st.date_input(
                        "Date of Birth *",
                        help="Enter complete date of birth"
                    )
                elif "Only year" in date_of_birth_indicator:
                    date_of_birth = st.text_input(
                        "Year of Birth *",
                        help="Enter year only",
                        placeholder="YYYY"
                    )
                else:  # Month and year
                    date_of_birth = st.text_input(
                        "Month and Year of Birth *",
                        help="Enter month and year",
                        placeholder="MM/YYYY"
                    )
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                place_of_birth = st.text_input(
                    "Place of Birth *",
                    help="Enter place of birth",
                    placeholder="e.g., Snowy Plain"
                )
            
            with col4:
                state_of_birth = st.text_input(
                    "State of Birth",
                    help="Enter state of birth",
                    placeholder="e.g., NSW"
                )
            
            with col5:
                country_of_birth = st.selectbox(
                    "Country of Birth *",
                    options=[
                        "Australia",
                        "New Zealand",
                        "United Kingdom",
                        "United States",
                        "Canada",
                        "Other"
                    ],
                    help="Select country of birth"
                )
            
            col6, col7 = st.columns(2)
            
            with col6:
                nationality_at_birth = st.text_input(
                    "Nationality at Birth *",
                    value="Australian",
                    help="Enter nationality at birth"
                )
        
        st.divider()
        
        # Additional Information Section
        st.subheader("ℹ️ Additional Information")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                residency_status = st.selectbox(
                    "Residency Status in Australia",
                    options=[
                        "Citizen",
                        "Permanent Resident",
                        "Temporary Resident",
                        "Visitor",
                        "Other"
                    ],
                    help="Select residency status"
                )
            
            with col2:
                civil_status = st.selectbox(
                    "Civil Status *",
                    options=[
                        "Single",
                        "Married",
                        "De Facto",
                        "Divorced",
                        "Widowed",
                        "Separated"
                    ],
                    help="Select civil status"
                )
            
            with col3:
                packaged_member_of_eu = st.selectbox(
                    "Privileged Member of EU?",
                    options=["No", "Yes"],
                    help="Is applicant a privileged member of EU?"
                )
            
            col4, col5 = st.columns(2)
            
            with col4:
                occupation = st.selectbox(
                    "Occupation *",
                    options=[
                        "Employed",
                        "Unemployed",
                        "Self-Employed",
                        "Student",
                        "Retired",
                        "Other"
                    ],
                    help="Select occupation status"
                )
        
        st.divider()
        
        # Form submission buttons
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            submit_button = st.form_submit_button(
                "💾 Save Application",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            draft_button = st.form_submit_button(
                "📝 Save as Draft",
                use_container_width=True
            )
        
        with col3:
            clear_button = st.form_submit_button(
                "🗑️ Clear Form",
                use_container_width=True
            )
    
    # Handle form submission
    if submit_button or draft_button:
        # Validate required fields
        required_fields = {
            "Given Name": given_name,
            "Surname": surname,
            "Case Type": case_type,
            "Application Type": application_type,
            "Visa Type": visa_type_requested,
            "Gender": gender,
            "Country of Nationality": country_of_nationality,
            "Street": street,
            "Postal Code": postal_code,
            "City": city,
            "Country": country,
            "Place of Birth": place_of_birth,
            "Country of Birth": country_of_birth,
            "Civil Status": civil_status,
            "Occupation": occupation
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        
        if missing_fields and submit_button:
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
        else:
            try:
                # Prepare application data
                application_data = {
                    'application_number': application_number if application_number else None,
                    'case_type': case_type,
                    'visa_type_requested': visa_type_requested,
                    'application_type': application_type,
                    'submission_date': submission_date.strftime("%d/%m/%Y"),
                    'intake_location': intake_location,
                    'applicant_is_minor': applicant_is_minor == "Yes",
                    'is_urgent': urgent == "Yes",
                    'given_name': given_name,
                    'surname': surname,
                    'surname_at_birth': surname_at_birth,
                    'variation_in_birth_certificate': variation_in_birth_certificate == "Yes",
                    'gender': gender,
                    'country_of_nationality': country_of_nationality,
                    'street_number': f"{street} {house_number}".strip(),
                    'unit_number': unit_number,
                    'postal_code': postal_code,
                    'city': city,
                    'country': country,
                    'date_of_birth': str(date_of_birth) if isinstance(date_of_birth, datetime) else date_of_birth,
                    'date_of_birth_indicator': date_of_birth_indicator,
                    'state_of_birth': state_of_birth,
                    'place_of_birth': place_of_birth,
                    'country_of_birth': country_of_birth,
                    'nationality_at_birth': nationality_at_birth,
                    'residency_status_in_australia': residency_status,
                    'civil_status': civil_status,
                    'packaged_member_of_eu': packaged_member_of_eu == "Yes",
                    'occupation': occupation,
                    'created_by': st.session_state.get('user', 'Unknown'),
                    'status': 'Draft' if draft_button else 'Submitted'
                }
                
                # Create application
                app_number = visa_service.create_application(application_data)
                
                if draft_button:
                    st.success(f"✅ Application saved as draft! Application Number: {app_number}")
                else:
                    st.success(f"✅ Application submitted successfully! Application Number: {app_number}")
                
                # Update activity after successful submission
                SessionManager.update_activity()
                
            except Exception as e:
                st.error(f"❌ Error saving application: {str(e)}")
    
    if clear_button:
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
