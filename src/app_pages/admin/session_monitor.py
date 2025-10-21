"""
Session Monitor Module
Handles session monitoring, cleanup, and directory management
"""

import streamlit as st
import os
import shutil
from datetime import datetime
import pandas as pd

from config.settings import Settings
from util.dutch_formatting_functions import format_dutch_date


def calculate_directory_size(path):
    """Calculate total size and file count of directory"""
    total_size = 0
    file_count = 0
    try:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
    except (OSError, PermissionError):
        pass
    return total_size, file_count


def format_file_size(bytes_size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def format_time_ago(timestamp):
    """Convert timestamp to human readable time ago"""
    now = datetime.now().timestamp()
    diff = now - timestamp
    
    if diff < 60:
        return f"{int(diff)}s ago"
    elif diff < 3600:
        return f"{int(diff/60)}m ago"
    elif diff < 86400:
        return f"{int(diff/3600)}h ago"
    else:
        return f"{int(diff/86400)}d ago"


def get_session_info():
    """Get information about all session directories"""
    # Use Settings class to get data directory path
    settings = Settings()  # No session_id needed for shared data path
    data_path = settings.DATA_DIR
    
    sessions = []
    
    if not os.path.exists(data_path):
        return sessions
    
    try:
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            
            # Skip if not a directory
            if not os.path.isdir(item_path):
                continue
            
            # Get directory stats
            creation_time = os.path.getctime(item_path)
            modified_time = os.path.getmtime(item_path)
            size, file_count = calculate_directory_size(item_path)
            
            sessions.append({
                'session_id': item,
                'session_id_short': item[:8] + '...' if len(item) > 12 else item,
                'created': datetime.fromtimestamp(creation_time),
                'modified': datetime.fromtimestamp(modified_time),
                'age': format_time_ago(creation_time),
                'last_activity': format_time_ago(modified_time),
                'size': size,
                'size_formatted': format_file_size(size),
                'file_count': file_count,
                'path': item_path
            })
    except (OSError, PermissionError):
        pass
    
    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x['created'], reverse=True)
    return sessions


def delete_session_directory(session_id):
    """Delete a specific session directory"""
    settings = Settings()
    session_path = os.path.join(settings.DATA_DIR, session_id)
    
    if os.path.exists(session_path):
        try:
            shutil.rmtree(session_path)
            return True, f"Session {session_id[:8]}... deleted successfully"
        except Exception as e:
            return False, f"Error deleting session: {str(e)}"
    return False, "Session directory not found"


def clear_all_sessions():
    """Clear all session directories"""
    settings = Settings()
    data_path = settings.DATA_DIR
    
    deleted_count = 0
    errors = []
    
    if not os.path.exists(data_path):
        return 0, ["Data directory not found"]
    
    try:
        for item in os.listdir(data_path):
            item_path = os.path.join(data_path, item)
            
            # Skip if not a directory
            if not os.path.isdir(item_path):
                continue
            
            try:
                shutil.rmtree(item_path)
                deleted_count += 1
            except Exception as e:
                errors.append(f"Error deleting {item}: {str(e)}")
                
    except Exception as e:
        errors.append(f"Error accessing data directory: {str(e)}")
    
    return deleted_count, errors


def clear_old_sessions(hours_old=1):
    """Clear session directories older than specified hours"""
    sessions = get_session_info()
    cutoff_time = datetime.now().timestamp() - (hours_old * 3600)
    
    deleted_count = 0
    errors = []
    
    for session in sessions:
        if session['created'].timestamp() < cutoff_time:
            success, message = delete_session_directory(session['session_id'])
            if success:
                deleted_count += 1
            else:
                errors.append(message)
    
    return deleted_count, errors


def session_monitor_section():
    """Session monitoring and cleanup interface"""
    st.subheader("📁 Session Directory Monitor")
    
    # Get session information
    sessions = get_session_info()
    
    if not sessions:
        st.info("No active session directories found.")
        return
    
    # Summary statistics
    total_sessions = len(sessions)
    total_size = sum(session['size'] for session in sessions)
    oldest_session = min(sessions, key=lambda x: x['created']) if sessions else None
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", total_sessions)
    with col2:
        st.metric("Total Size", format_file_size(total_size))
    with col3:
        if oldest_session:
            st.metric("Oldest Session", oldest_session['age'])
    
    st.divider()
    
    # Sessions table
    st.subheader("Session Directories")
    
    # Create dataframe for display
    table_data = []
    for session in sessions:
        table_data.append({
            'Session ID': session['session_id_short'],
            'Created': format_dutch_date(session['created'], include_time=True),
            'Age': session['age'],
            'Last Activity': session['last_activity'],
            'Size': session['size_formatted'],
            'Files': session['file_count']
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch", hide_index=True)
        
        # Individual session actions
        st.subheader("Individual Actions")
        session_to_delete = st.selectbox(
            "Select session to delete:",
            options=[''] + [s['session_id'] for s in sessions],
            format_func=lambda x: f"{x[:8]}... ({next((s['age'] for s in sessions if s['session_id'] == x), '')})" if x else "Select a session..."
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Delete Selected", disabled=not session_to_delete):
                if session_to_delete:
                    success, message = delete_session_directory(session_to_delete)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        
        # Bulk actions
        st.divider()
        st.subheader("Bulk Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Clear Old Sessions (>1h)", type="secondary"):
                if st.session_state.get('confirm_old_cleanup') != True:
                    st.session_state['confirm_old_cleanup'] = True
                    st.warning("⚠️ Click again to confirm deletion of sessions older than 1 hour")
                else:
                    deleted_count, errors = clear_old_sessions(hours_old=1)
                    st.session_state['confirm_old_cleanup'] = False
                    if errors:
                        st.error(f"Deleted {deleted_count} sessions with errors: " + ", ".join(errors))
                    else:
                        st.success(f"Successfully deleted {deleted_count} old sessions")
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All Sessions", type="secondary"):
                if st.session_state.get('confirm_all_cleanup') != True:
                    st.session_state['confirm_all_cleanup'] = True
                    st.warning("⚠️ Click again to confirm deletion of ALL session directories")
                else:
                    deleted_count, errors = clear_all_sessions()
                    st.session_state['confirm_all_cleanup'] = False
                    if errors:
                        st.error(f"Deleted {deleted_count} sessions with errors: " + ", ".join(errors))
                    else:
                        st.success(f"Successfully deleted {deleted_count} sessions")
                    st.rerun()
        
        # Refresh button
        st.divider()
        if st.button("🔄 Refresh", help="Refresh the session list"):
            st.rerun()
    else:
        st.info("No session data to display")