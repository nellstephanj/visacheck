# src/config/settings.py

import os

class Settings:
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.initialize_paths()

    def initialize_paths(self):
        # Pointing to project directory
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.PROMPT_DIR = os.path.join(self.BASE_DIR, 'src', 'config', 'prompts')
        
        # Shared resource directories (no session required)
        self.RES_DIR = os.path.join(self.BASE_DIR, 'res')
        self.RES_DEMO_DIR = os.path.join(self.RES_DIR, 'demo')
        self.RES_IMG_DIR = os.path.join(self.RES_DIR, 'img')
        self.PEOPLE_DIR = os.path.join(self.RES_DIR, 'people')
        
        # Session-specific directories (only created if session_id provided)
        if self.session_id:
            self.SESSION_DIR = os.path.join(self.DATA_DIR, self.session_id)
            self.RAW_DATA_DIR = os.path.join(self.SESSION_DIR, 'raw')
            self.PROCESSED_DATA_DIR = os.path.join(self.SESSION_DIR, 'processed')
        else:
            # These will be None if no session_id - accessing them should raise an error
            self.SESSION_DIR = None
            self.RAW_DATA_DIR = None
            self.PROCESSED_DATA_DIR = None
        
        # Session-dependent subdirectories (only if session_id provided)
        if self.session_id:
            self.AUDIO_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'audio')
            self.JSON_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'json')
            self.TEXT_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'text')
            self.VIDEO_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'video')
            self.SCREENSHOT_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'screenshots')
        else:
            self.AUDIO_DIR = None
            self.JSON_DIR = None
            self.TEXT_DIR = None
            self.VIDEO_DIR = None
            self.SCREENSHOT_DIR = None
        
        self.ensure_directories()

    def ensure_directories(self):
        # Always create shared directories
        shared_dirs = [
            self.DATA_DIR, self.PROMPT_DIR,
            self.RES_DIR, self.RES_DEMO_DIR, self.RES_IMG_DIR, self.PEOPLE_DIR
        ]
        
        # Only create session-specific directories if session_id is provided
        session_dirs = []
        if self.session_id:
            session_dirs = [
                self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR,
                self.AUDIO_DIR, self.VIDEO_DIR, self.JSON_DIR, self.TEXT_DIR,
                self.SCREENSHOT_DIR
            ]
        
        for directory in shared_dirs + session_dirs:
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

