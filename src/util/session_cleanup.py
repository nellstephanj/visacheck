import os
import time
import shutil
import streamlit as st
import atexit
from typing import List, Tuple
from config.settings import Settings
from apscheduler.schedulers.background import BackgroundScheduler

# Import at module level to avoid circular imports
from util.session_manager import SessionManager

class SessionCleanup:
    """Background cleanup utility for abandoned session directories"""
    
    @staticmethod
    def cleanup_abandoned_sessions() -> Tuple[int, List[str]]:
        """
        Clean up session directories older than configured max age
        
        Returns:
            Tuple of (cleaned_count, list_of_cleaned_session_ids)
        """
        try:
            # Get cleanup time from environment variable (default 30 minutes)
            max_age_minutes = int(os.getenv("SESSION_CLEANUP_MINUTES", "30"))
            
            settings = Settings()  # No session_id needed for shared data path
            data_path = settings.DATA_DIR
            
            if not os.path.exists(data_path):
                return 0, []
            
            cutoff_time = time.time() - (max_age_minutes * 60)
            cleaned_sessions = []
            cleaned_count = 0
            
            # Scan all directories in data path
            for item in os.listdir(data_path):
                item_path = os.path.join(data_path, item)
                
                # Skip if not a directory
                if not os.path.isdir(item_path):
                    continue
                    
                # Check if directory is old enough to clean
                if SessionCleanup._should_cleanup_session(item_path, cutoff_time):
                    try:
                        # Delete the session directory
                        shutil.rmtree(item_path)
                        
                        cleaned_sessions.append(item)
                        cleaned_count += 1
                        
                        print(f"Cleaned abandoned session: {item}")
                        
                    except (OSError, PermissionError) as e:
                        print(f"Error cleaning session {item}: {e}")
                        continue
            
            if cleaned_count > 0:
                print(f"Cleanup completed: {cleaned_count} sessions cleaned (max age: {max_age_minutes} minutes)")
            else:
                print(f"Cleanup completed: No abandoned sessions found (max age: {max_age_minutes} minutes)")
                
            return cleaned_count, cleaned_sessions
            
        except Exception as e:
            print(f"Error during session cleanup: {e}")
            return 0, []
    
    @staticmethod
    def _should_cleanup_session(session_path: str, cutoff_time: float) -> bool:
        """
        Determine if a session directory should be cleaned up based on activity file
        
        Args:
            session_path: Path to session directory
            cutoff_time: Time threshold for cleanup
            
        Returns:
            True if session should be cleaned up
        """
        try:
            last_activity_time = SessionManager.get_session_last_activity_time(session_path)
            return last_activity_time < cutoff_time
            
        except Exception:
            # If we can't determine activity time, don't clean it (safe default)
            return False
    
    @staticmethod
    @st.cache_resource(ttl=None)  # Singleton for app lifetime
    def get_background_scheduler():
        """
        Create and return a singleton BackgroundScheduler instance.
        This ensures only one scheduler runs across all user sessions.
        """
        print("Initializing singleton background scheduler...")
        
        # Get cleanup frequency from environment variable (default 15 minutes)
        cleanup_frequency_minutes = int(os.getenv("SESSION_CLEANUP_FREQUENCY_MINUTES", "15"))
        
        # Create scheduler
        scheduler = BackgroundScheduler()
        
        # Add session cleanup job
        scheduler.add_job(
            SessionCleanup.cleanup_abandoned_sessions,
            'interval',
            minutes=cleanup_frequency_minutes,
            max_instances=1,  # Prevent overlapping runs
            id='session_cleanup',
            name='Session Cleanup Task'
        )
        
        # Start scheduler
        try:
            scheduler.start()
            print(f"✅ Background session cleanup scheduler started (runs every {cleanup_frequency_minutes} minutes)")
            
            # Register shutdown handler to clean up scheduler on app exit
            def shutdown_scheduler():
                if scheduler.running:
                    scheduler.shutdown(wait=False)
                    print("Background scheduler shutdown complete")
            
            atexit.register(shutdown_scheduler)
            
        except Exception as e:
            print(f"❌ Failed to start cleanup scheduler: {e}")
            raise
        
        return scheduler
    
    @staticmethod
    def ensure_scheduler_running():
        """
        Ensure the singleton scheduler is running.
        Call this from your main app to initialize the scheduler.
        """
        try:
            scheduler = SessionCleanup.get_background_scheduler()
            if not scheduler.running:
                print("Scheduler was not running, attempting to restart...")
                scheduler.start()
            return scheduler
        except Exception as e:
            print(f"Error ensuring scheduler is running: {e}")
            return None