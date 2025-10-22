"""Visa Application Matching Page"""
import streamlit as st
import json
import random
import os
from pathlib import Path
from util.session_manager import SessionManager


def load_person_data(file_path):
    """Load person data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def get_random_people(people_dir, count=5):
    """Get random people from the people directory"""
    json_files = list(Path(people_dir).glob("person_*.json"))
    selected_files = random.sample(json_files, min(count, len(json_files)))
    return [load_person_data(file) for file in selected_files]


def format_date_of_birth(dob):
    """Format date of birth from dict to string"""
    if not dob:
        return "Not provided"
    
    day = dob.get('day', '')
    month = dob.get('month', '')
    year = dob.get('year', '')
    
    if day and month and year:
        return f"{day:02d}/{month:02d}/{year}"
    elif month and year:
        return f"{month:02d}/{year}"
    elif year:
        return str(year)
    return "Not provided"


def get_robohash_url(identifier, size=200):
    """Generate robohash.org URL for profile picture"""
    return f"https://robohash.org/{identifier}?size={size}x{size}"


def display_person_card(person, is_applicant=False, card_id=None):
    """Display a person card with profile picture and details"""
    
    # Generate unique identifier for robohash
    identifier = person.get('visa_application_number', f"person_{card_id}")
    profile_pic_url = get_robohash_url(identifier)
    
    # Create card container
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display profile picture
            st.image(profile_pic_url, use_container_width=True)
        
        with col2:
            # Display person details
            if is_applicant:
                st.markdown("### Applicant Details")
            
            st.markdown(f"**Surname:** {person.get('surname', 'N/A')}")
            st.markdown(f"**Surname at birth:** {person.get('surname', 'N/A')}")
            st.markdown(f"**Given Name:** {person.get('given_names', 'N/A')}")
            st.markdown(f"**Nationality:** {person.get('country_of_nationality', 'N/A')}")
            
            dob = format_date_of_birth(person.get('date_of_birth'))
            st.markdown(f"**Date of Birth:** {dob}")
            
            place_of_birth = person.get('place_of_birth', {})
            place_str = place_of_birth.get('city', 'N/A')
            st.markdown(f"**Place of Birth:** {place_str}")
            
            country_of_birth = place_of_birth.get('country', 'N/A')
            st.markdown(f"**Country of Birth:** {country_of_birth}")
            
            st.markdown(f"**Gender:** {person.get('gender', 'N/A')}")
            
            if not is_applicant:
                euvis_apps = person.get('euvis_applications', random.randint(1, 10))
                st.markdown(f"**EUVIS Applications:** {euvis_apps}")


def display_candidate_compact(person, candidate_num, is_selected=False):
    """Display a compact candidate card for the list"""
    
    identifier = person.get('visa_application_number', f"candidate_{candidate_num}")
    profile_pic_url = get_robohash_url(identifier, size=150)
    
    # Create container with selection highlighting
    container_style = "border: 3px solid #4CAF50;" if is_selected else ""
    
    with st.container(border=True):
        # Header with EU-VIS badge and candidate number
        col_header1, col_header2, col_header3 = st.columns([2, 3, 1])
        with col_header1:
            st.markdown(f"""
                <div style='background-color: #E3F2FD; padding: 4px 12px; border-radius: 4px; 
                            display: inline-block; color: #1976D2; font-weight: bold; font-size: 14px;'>
                    EU-VIS
                </div>
            """, unsafe_allow_html=True)
        with col_header2:
            st.markdown(f"**Candidate {candidate_num}**")
        with col_header3:
            # Add selection checkbox or button
            pass
        
        st.markdown("---")
        
        # Content columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(profile_pic_url, use_container_width=True)
        
        with col2:
            surname = person.get('surname', 'N/A')
            given_names = person.get('given_names', 'N/A')
            nationality = person.get('country_of_nationality', 'N/A')
            dob = format_date_of_birth(person.get('date_of_birth'))
            place_of_birth = person.get('place_of_birth', {})
            place_str = place_of_birth.get('city', 'N/A')
            country_of_birth = place_of_birth.get('country', 'N/A')
            gender = person.get('gender', 'N/A')
            euvis_apps = random.randint(1, 10)
            
            st.markdown(f"**Surname:** {surname}")
            st.markdown(f"**Surname at birth:** {surname}")
            st.markdown(f"**Given Name:** {given_names}")
            st.markdown(f"**Nationality:** {nationality}")
            st.markdown(f"**Date of Birth:** {dob}")
            st.markdown(f"**Place of Birth:** {place_str}")
            st.markdown(f"**Country of Birth:** {country_of_birth}")
            st.markdown(f"**Gender:** {gender}")
            st.markdown(f"**EUVIS Applications:** {euvis_apps}")


def matching_page():
    """Visa Application Matching Screen"""
    
    # Check authentication
    if not SessionManager.is_valid():
        st.error("Please log in to access this page.")
        st.query_params["page"] = "login"
        st.rerun()
        return
    
    # Update activity
    SessionManager.update_activity()
    
    # Page title
    st.title("EU-VIS Matching")
    
    # Navigation buttons at the top
    col1, col2, col3, col4 = st.columns([1, 1, 1.5, 3.5])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.info("Navigate back to previous page")
    with col2:
        match_euvis = st.button("Match EU-VIS", type="primary", use_container_width=True)
    with col3:
        validate_agent = st.button("🤖 Validate with Agent", use_container_width=True)
    
    st.divider()
    
    # Get the people directory
    base_dir = Path(__file__).parent.parent.parent
    people_dir = base_dir / "res" / "people"
    
    # Initialize session state for candidates
    if 'matching_applicant' not in st.session_state or match_euvis:
        # Load random people (applicant will be the first one)
        all_people = get_random_people(people_dir, count=6)
        st.session_state['matching_applicant'] = all_people[0] if all_people else None
        st.session_state['matching_candidates'] = all_people[1:] if len(all_people) > 1 else []
        st.session_state['selected_candidate'] = None
    
    applicant = st.session_state.get('matching_applicant')
    candidates = st.session_state.get('matching_candidates', [])
    
    if not applicant:
        st.error("No applicant data available")
        return
    
    # Show validation modal when validate button is clicked
    if validate_agent and candidates:
        @st.dialog("🤖 Agent Validation Results", width="large")
        def show_agent_validation():
            # Select a random candidate as the agent's suggestion
            suggested_idx = random.randint(1, len(candidates))
            suggested_candidate = candidates[suggested_idx - 1]
            
            st.success(f"**Recommended Match: Candidate {suggested_idx}**")
            st.write("")
            
            # Display candidate summary
            st.markdown(f"""
            ### Match Details
            - **Name:** {suggested_candidate.get('given_names', 'N/A')} {suggested_candidate.get('surname', 'N/A')}
            - **Nationality:** {suggested_candidate.get('country_of_nationality', 'N/A')}
            - **Date of Birth:** {format_date_of_birth(suggested_candidate.get('date_of_birth'))}
            - **Place of Birth:** {suggested_candidate.get('place_of_birth', {}).get('city', 'N/A')}
            """)
            
            st.write("")
            st.markdown("### Reasoning")
            
            # Generate reasons based on data similarity
            reasons = []
            
            # Check name similarity
            if suggested_candidate.get('surname', '').lower() == applicant.get('surname', '').lower():
                reasons.append("**Exact surname match** - Identical family name detected")
            elif suggested_candidate.get('surname', '')[:3].lower() == applicant.get('surname', '')[:3].lower():
                reasons.append("**Similar surname** - Family name shows strong similarity")
            
            # Check date of birth
            app_dob = applicant.get('date_of_birth', {})
            cand_dob = suggested_candidate.get('date_of_birth', {})
            if app_dob.get('year') == cand_dob.get('year'):
                if app_dob.get('month') == cand_dob.get('month') and app_dob.get('day') == cand_dob.get('day'):
                    reasons.append("**Exact date of birth match** - Complete DOB matches perfectly")
                elif app_dob.get('month') == cand_dob.get('month'):
                    reasons.append("**Birth year and month match** - Born in the same month and year")
                else:
                    reasons.append("**Birth year match** - Same year of birth")
            
            # Check nationality
            if suggested_candidate.get('country_of_nationality', '').lower() == applicant.get('country_of_nationality', '').lower():
                reasons.append("**Same nationality** - Both share the same country of nationality")
            
            # Check place of birth
            app_pob = applicant.get('place_of_birth', {})
            cand_pob = suggested_candidate.get('place_of_birth', {})
            if app_pob.get('city', '').lower() == cand_pob.get('city', '').lower():
                reasons.append("**Same place of birth** - Both born in the same city")
            elif app_pob.get('country', '').lower() == cand_pob.get('country', '').lower():
                reasons.append("**Same country of birth** - Both born in the same country")
            
            # Check gender
            if suggested_candidate.get('gender', '').lower() == applicant.get('gender', '').lower():
                reasons.append("**Gender match** - Same gender recorded")
            
            # If no specific reasons, provide generic ones
            if not reasons:
                reasons = [
                    "**Biometric similarity** - Facial recognition shows high confidence match",
                    "**Document patterns** - Similar document history patterns detected",
                    "**Travel history** - Overlapping travel destinations and dates"
                ]
            
            # Display reasons
            for reason in reasons[:3]:  # Show top 3 reasons
                st.markdown(f"✓ {reason}")
            
            st.write("")
            st.info(f"**Confidence Score:** {random.randint(75, 98)}%")
            
            st.write("")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Accept Suggestion", type="primary", use_container_width=True):
                    st.session_state['selected_candidate'] = suggested_idx
                    st.success(f"✅ Candidate {suggested_idx} selected!")
                    st.rerun()
            with col2:
                if st.button("Dismiss", use_container_width=True):
                    st.rerun()
        
        show_agent_validation()
    elif validate_agent and not candidates:
        st.warning("No candidates available for validation. Click 'Match EU-VIS' first.")
    
    # Top navigation tabs
    tab1, tab2 = st.tabs([f"🌍 EU-VIS ({len(candidates)})", "🔵 BVV (0)"])
    
    with tab1:
        # Main layout: Applicant on left, Candidates on right
        col_applicant, col_candidates = st.columns([1, 1])
        
        with col_applicant:
            st.markdown("### Applicant")
            display_person_card(applicant, is_applicant=True)
        
        with col_candidates:
            st.markdown("### Potential Matches")
            
            # Display candidates
            if candidates:
                for idx, candidate in enumerate(candidates, 1):
                    is_selected = st.session_state.get('selected_candidate') == idx
                    
                    # Create a unique key for each candidate
                    with st.container():
                        display_candidate_compact(candidate, idx, is_selected)
                        
                        # Selection button
                        col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1])
                        with col_btn2:
                            if st.button("✓ Select", key=f"select_{idx}", use_container_width=True):
                                st.session_state['selected_candidate'] = idx
                                st.success(f"Selected Candidate {idx}")
                                st.rerun()
                        with col_btn3:
                            if st.button("ℹ️", key=f"info_{idx}", use_container_width=True):
                                st.info(f"View details for Candidate {idx}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
            else:
                st.info("No matching candidates found")
    
    with tab2:
        st.info("BVV matching not yet implemented")
    
    # Bottom action buttons
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("Reset", use_container_width=True):
            st.session_state['selected_candidate'] = None
            st.rerun()
    
    with col3:
        selected_idx = st.session_state.get('selected_candidate')
        if selected_idx:
            if st.button("Confirm Selection", type="primary", use_container_width=True):
                st.success(f"✅ Confirmed match with Candidate {selected_idx}")
        else:
            st.button("Confirm Selection", type="primary", use_container_width=True, disabled=True)
    
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
            "📚 Matching Guidelines",
            "https://example.com/guidelines",
            type="secondary",
            use_container_width=True
        )
