import streamlit as st
import time
import os
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from util.user_functions import UserHandler


class SessionManager:
    """Centralized session management for the application"""
    
    REQUIRED_KEYS = ['user', 'user_engagement', 'login-timestamp', 'is_admin']
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT_SECONDS", "1800"))  # Default 30 minutes in seconds
    WARNING_TIME = int(os.getenv("SESSION_WARNING_SECONDS", "1200"))     # Default 20 minutes - show warning
    
    @staticmethod
    def initialize_session(user, user_engagement: str, is_admin: bool):
        """Initialize a new user session with all required state variables"""
        current_time = time.time()
        st.session_state['user'] = user
        st.session_state['user_engagement'] = user_engagement
        st.session_state['login-timestamp'] = current_time
        st.session_state['last_activity_time'] = current_time  # Initialize activity tracking
        st.session_state['is_admin'] = is_admin
        
        # Initialize other session variables if they don't exist
        if 'session_id' not in st.session_state:
            import uuid
            st.session_state['session_id'] = str(uuid.uuid4())
        if 'video_segment_valid' not in st.session_state:
            st.session_state['video_segment_valid'] = True
        if 'processed_files' not in st.session_state:
            st.session_state['processed_files'] = []
        if 'help_shown' not in st.session_state:
            st.session_state['help_shown'] = False
        if 'is_processing' not in st.session_state:
            st.session_state['is_processing'] = False
        if 'progress_tracker' not in st.session_state:
            st.session_state['progress_tracker'] = None
        
        # Create initial activity file
        SessionManager._write_activity_file(current_time)
        
    
    @staticmethod
    def update_activity():
        """Update user activity timestamp in session state and activity file"""
        if not SessionManager.is_authenticated():
            return
        
        current_time = time.time()
        st.session_state['last_activity_time'] = current_time
        
        # Ensure activity file exists, then update it
        SessionManager._ensure_activity_file_exists(current_time)
        SessionManager._write_activity_file(current_time)
    
    @staticmethod
    def _ensure_activity_file_exists(timestamp: float):
        """Ensure activity file exists, create it if it doesn't"""
        if 'session_id' not in st.session_state or not st.session_state['session_id']:
            return
            
        try:
            from config.settings import Settings
            settings = Settings(session_id=st.session_state['session_id'])
            
            # Use Settings SESSION_DIR for proper path construction
            activity_file_path = os.path.join(settings.SESSION_DIR, 'last_activity.txt')
            
            # Check if activity file exists
            if not os.path.exists(activity_file_path):
                # Settings.ensure_directories() should have created SESSION_DIR already
                # but let's be safe
                if not os.path.exists(settings.SESSION_DIR):
                    os.makedirs(settings.SESSION_DIR, exist_ok=True)
                
                # Create the activity file with current timestamp
                with open(activity_file_path, 'w') as f:
                    f.write(str(timestamp))
                    
        except Exception as e:
            # Don't crash if file creation fails, just continue silently
            # Activity tracking will still work in-memory
            pass
    
    @staticmethod
    def _write_activity_file(timestamp: float):
        """Write activity timestamp to session directory for background cleanup"""
        try:
            if 'session_id' in st.session_state and st.session_state['session_id']:
                from config.settings import Settings
                settings = Settings(session_id=st.session_state['session_id'])
                
                # Use Settings SESSION_DIR for proper path construction
                activity_file_path = os.path.join(settings.SESSION_DIR, 'last_activity.txt')
                
                # Write timestamp to activity file (SESSION_DIR should already exist from Settings)
                with open(activity_file_path, 'w') as f:
                    f.write(str(timestamp))
        except Exception as e:
            # Don't crash if file write fails, just continue silently
            # Session management will still work, cleanup might be less accurate
            pass
    
    @staticmethod
    def clear_session():
        """Safely clear all session data and clean up session directory"""
        # Clean up session directory if it exists
        if 'session_id' in st.session_state and st.session_state['session_id']:
            try:
                from config.settings import Settings
                from util.manual_functions import ManualHandler
                settings = Settings(session_id=st.session_state['session_id'])
                ManualHandler.clear_local_folders(settings)
            except Exception as e:
                print(f"Error cleaning session directory during logout: {e}")
        
        keys_to_clear = [
            'user', 'user_engagement', 'login-timestamp', 'is_admin',
            'session_id', 'video_segment_valid', 'processed_files', 'help_shown',
            'last_activity_time',  # Clear activity tracking data
            'is_processing',       # Clear processing state
            'progress_tracker'     # Clear progress tracker
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def is_valid() -> bool:
        """Validate that all required session keys exist and have values"""
        for key in SessionManager.REQUIRED_KEYS:
            if key not in st.session_state or st.session_state[key] is None:
                return False
        return True
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is properly authenticated"""
        return SessionManager.is_valid()
    
    @staticmethod
    def check_timeout() -> tuple[bool, Optional[str]]:
        """
        Check session timeout based on last activity time and return status
        Returns: (is_valid, warning_message)
        """
        # Use last_activity_time if available, fall back to login-timestamp
        activity_time_key = "last_activity_time" if "last_activity_time" in st.session_state else "login-timestamp"
        
        if activity_time_key not in st.session_state:
            return False, None
            
        time_elapsed = time.time() - st.session_state[activity_time_key]
        
        if time_elapsed >= SessionManager.SESSION_TIMEOUT:
            SessionManager.clear_session()  # This now also cleans up directories
            return False, "Session expired due to inactivity. Please log in again."
        elif time_elapsed >= SessionManager.WARNING_TIME:
            remaining_minutes = int((SessionManager.SESSION_TIMEOUT - time_elapsed) / 60)
            warning_msg = f"⚠️ Session will expire in {remaining_minutes} minute(s) due to inactivity"
            return True, warning_msg
        
        return True, None
    
    @staticmethod
    def recover_session_state(user_handler) -> bool:
        """
        Attempt to recover session state if user exists but other data is missing
        Returns True if recovery successful, False otherwise
        """
        if 'user' in st.session_state and st.session_state['user'] and str(st.session_state['user']).strip():
            try:
                user = user_handler.get_user(st.session_state['user'])
                if user:
                    # Recover missing session data
                    if 'user_engagement' not in st.session_state:
                        st.session_state['user_engagement'] = user.engagement
                    if 'is_admin' not in st.session_state:
                        st.session_state['is_admin'] = user.isAdmin
                    if 'login-timestamp' not in st.session_state:
                        current_time = time.time()
                        st.session_state['login-timestamp'] = current_time
                        st.session_state['last_activity_time'] = current_time
                        # Create activity file for recovered session
                        SessionManager._write_activity_file(current_time)
                    
                    return True
            except Exception:
                # If user lookup fails, clear the corrupted session
                SessionManager.clear_session()
        
        return False
    
    @staticmethod
    def get_user_info() -> dict:
        """Get current user information from session"""
        if not SessionManager.is_valid():
            return {}
        
        return {
            'user': st.session_state['user'],
            'user_engagement': st.session_state['user_engagement'],
            'is_admin': st.session_state['is_admin'],
            'login_time': st.session_state['login-timestamp'],
            'last_activity_time': st.session_state.get('last_activity_time', st.session_state['login-timestamp'])
        }
    
    @staticmethod
    def require_admin() -> bool:
        """Check if current user has admin privileges"""
        return SessionManager.is_authenticated() and st.session_state.get('is_admin', False)
    
    @staticmethod
    def get_session_last_activity_time(session_path: str) -> float:
        """
        Get the last activity timestamp for a session directory
        
        Args:
            session_path: Path to session directory
            
        Returns:
            Last activity timestamp from last_activity.txt, or directory modification time as fallback
        """
        try:
            # Check for activity file first (preferred method)
            activity_file_path = os.path.join(session_path, 'last_activity.txt')
            
            if os.path.exists(activity_file_path):
                # Read last activity time from activity file
                with open(activity_file_path, 'r') as f:
                    last_activity_time = float(f.read().strip())
                return last_activity_time
            
        except (OSError, PermissionError, ValueError):
            pass
        
        # Fallback to directory modification time
        try:
            return os.path.getmtime(session_path)
        except (OSError, PermissionError):
            # If we can't access the directory at all, return current time
            return time.time()