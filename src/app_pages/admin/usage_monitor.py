"""
Usage Monitor Module
Handles usage monitoring, reporting, and Excel export functionality
"""

import streamlit as st
import os
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import month_name
import pandas as pd

from util.azure_functions import AzureHandler
from util.dutch_formatting_functions import format_dutch_number


def get_month_options():
    """Generate list of available months for the dropdown"""
    current_date = datetime.now()
    months = []
    
    for i in range(12):  # Last 12 months
        month_date = current_date - relativedelta(months=i)
        month_str = month_date.strftime("%Y-%m")
        month_display = f"{month_name[month_date.month]} {month_date.year}"
        months.append((month_str, month_display))
    
    return months


def parse_usage_logs(azure_handler: AzureHandler, target_month=None, engagement_filter=None):
    """
    Retrieve and parse usage logs from Azure table
    Returns aggregated usage data by user and engagement
    """
    try:
        # Get all usage logs
        filter_query = None
        if target_month:
            # Filter by month in RowKey (timestamp)
            start_date = f"{target_month}-01T00:00:00"
            next_month = datetime.strptime(target_month + "-01", "%Y-%m-%d") + relativedelta(months=1)
            end_date = next_month.strftime("%Y-%m-%dT00:00:00")
            filter_query = f"RowKey ge '{start_date}' and RowKey lt '{end_date}'"
        
        if engagement_filter and engagement_filter != "All":
            engagement_filter_query = f"PartitionKey eq '{engagement_filter}'"
            if filter_query:
                filter_query = f"{filter_query} and {engagement_filter_query}"
            else:
                filter_query = engagement_filter_query
        
        usage_logs = azure_handler.retrieve_table_items("UsageLogs", filter_query)
        
        if not usage_logs:
            return [], {}
        
        # Convert ItemPaged to list for proper iteration
        usage_logs_list = list(usage_logs)
        
        if not usage_logs_list:
            return [], {}
        
        # Process and aggregate data
        user_data = {}
        
        for log in usage_logs_list:
            username = log.get('UserName', 'Unknown')
            engagement = log.get('PartitionKey', 'Unknown')
            usage_unit = log.get('UsageUnit', '')
            usage_amount = float(log.get('UsageAmount', 0))
            
            # Create unique key for user-engagement combination
            user_key = f"{username}|{engagement}"
            
            if user_key not in user_data:
                user_data[user_key] = {
                    'username': username,
                    'engagement': engagement,
                    'input_tokens': 0,
                    'output_tokens': 0,
                    'whisper_seconds': 0
                }
            
            # Aggregate by usage type
            if usage_unit == "Input tokens":
                user_data[user_key]['input_tokens'] += usage_amount
            elif usage_unit == "Output tokens":
                user_data[user_key]['output_tokens'] += usage_amount
            elif usage_unit == "Seconds":
                user_data[user_key]['whisper_seconds'] += usage_amount
        
        # Convert to list and calculate totals
        user_list = list(user_data.values())
        
        # Calculate summary totals
        summary = {
            'total_input_tokens': sum(user['input_tokens'] for user in user_list),
            'total_output_tokens': sum(user['output_tokens'] for user in user_list),
            'total_whisper_seconds': sum(user['whisper_seconds'] for user in user_list)
        }
        
        return user_list, summary
        
    except Exception as e:
        st.error(f"Error retrieving usage data: {str(e)}")
        return [], {}


def create_excel_report(user_data, summary, month_display, engagement_filter):
    """Create Excel report with usage data"""
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': [
                    'Report Period', 
                    'Engagement Filter', 
                    'Total Users',
                    'Total Input Tokens', 
                    'Total Output Tokens', 
                    'Total Duration (seconds)',
                    'Total Duration (minutes)'
                ],
                'Value': [
                    month_display,
                    engagement_filter,
                    len(user_data),  # Calculate total users from user_data length
                    format_dutch_number(summary['total_input_tokens']),
                    format_dutch_number(summary['total_output_tokens']),
                    format_dutch_number(summary['total_whisper_seconds'], 1),
                    format_dutch_number(summary['total_whisper_seconds']/60, 1)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed data sheet
            if user_data:
                detailed_data = []
                for user in user_data:
                    detailed_data.append({
                        'User': user['username'],
                        'Engagement': user['engagement'],
                        'Input Tokens': format_dutch_number(user['input_tokens']),
                        'Output Tokens': format_dutch_number(user['output_tokens']),
                        'Duration (seconds)': format_dutch_number(user['whisper_seconds'], 1),
                        'Duration (minutes)': format_dutch_number(user['whisper_seconds']/60, 1)
                    })
                
                detailed_df = pd.DataFrame(detailed_data)
                detailed_df.to_excel(writer, sheet_name='User Details', index=False)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error creating Excel report: {str(e)}")
        return None


def usage_monitor_section(azure_handler: AzureHandler, get_engagements_func):
    """Usage monitoring and reporting interface"""
    st.header("📊 Usage Monitor")
    
    # Month and engagement selection
    col1, col2 = st.columns(2)
    
    with col1:
        month_options = get_month_options()
        selected_month_tuple = st.selectbox(
            "Select Month",
            options=month_options,
            format_func=lambda x: x[1],  # Display the formatted month name
            index=0  # Default to current month
        )
        selected_month = selected_month_tuple[0]  # Get the YYYY-MM format
        month_display = selected_month_tuple[1]   # Get the display format
    
    with col2:
        engagements = get_engagements_func(azure_handler)
        engagement_filter = st.selectbox(
            "Filter by Engagement",
            options=["All"] + engagements,
            index=0
        )
    
    # Get usage data
    user_data, summary = parse_usage_logs(azure_handler, selected_month, engagement_filter)
    
    if not user_data and not summary:
        st.info("No usage data found for the selected period and filters.")
        return
    
    st.divider()
    
    # Summary metrics in a nice container
    with st.container():
        st.subheader("📈 Usage Summary")
        
        # Get model names from environment variables
        llm_model = os.getenv("MODEL_NAME_LLM", "GPT Model")
        transcription_model = os.getenv("MODEL_NAME_TRANSCRIPTION", "Transcription Model")
        
        # Create metrics with better styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**🤖 {llm_model}**")
            with st.container(border=True):
                st.metric(
                    label="Input Tokens",
                    value=format_dutch_number(summary['total_input_tokens']),
                    help="Total input tokens consumed by the LLM"
                )
        
        with col2:
            st.markdown(f"**🤖 {llm_model}**")
            with st.container(border=True):
                st.metric(
                    label="Output Tokens",
                    value=format_dutch_number(summary['total_output_tokens']),
                    help="Total output tokens generated by the LLM"
                )
        
        with col3:
            st.markdown(f"**🎙️ {transcription_model}**")
            with st.container(border=True):
                st.metric(
                    label="Duration",
                    value=f"{format_dutch_number(summary['total_whisper_seconds']/60, 1)} min",
                    help="Total transcription duration in minutes"
                )
    
    st.divider()
    
    # User Breakdown - moved here after Usage Summary
    if user_data:
        st.subheader("👥 User Breakdown")
        
        # Create display dataframe
        table_data = []
        for user in user_data:
            table_data.append({
                'User': user['username'],
                'Engagement': user['engagement'],
                'Input Tokens': format_dutch_number(user['input_tokens']),
                'Output Tokens': format_dutch_number(user['output_tokens']),
                'Duration (min)': format_dutch_number(user['whisper_seconds']/60, 1)
            })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, width="stretch", hide_index=True)
    
    else:
        st.info("No detailed user data available for the selected filters.")
    
    # Export functionality - moved to bottom
    st.divider()
    st.subheader("📄 Export Report")
    
    # Direct download button - generates and downloads in one click
    excel_data = create_excel_report(user_data, summary, month_display, engagement_filter)
    
    if excel_data:
        filename = f"VisaCheck_Usage_{month_display}_{engagement_filter}.xlsx".replace(' ', '_').replace('|', '_')
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            width="stretch"
        )
    else:
        st.error("Unable to generate Excel report. Please try again.")
    
    # Report details below the button
    st.write(f"**Report Details:** VisaCheck Usage | {month_display} | {engagement_filter}")