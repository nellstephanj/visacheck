import streamlit as st
import time


class VideoProgressTracker:
    """Tracks and displays progress for video documentation generation"""
    
    STEPS = [
        "🎵 Extracting audio from video...",
        "🔄 Converting audio format...", 
        "📝 Transcribing audio to text...",
        "📖 Generating documentation...",
        "📸 Extracting screenshots...",
        "✨ Finalizing documentation..."
    ]
    
    def __init__(self):
        self.progress_bar = None
        self.current_step = 0
        
    def initialize(self):
        """Create and initialize the progress bar"""
        self.progress_bar = st.progress(0, text=self.STEPS[0])
        self.current_step = 0
        
    def update_step(self, step_index):
        """Update progress to the specified step"""
        if self.progress_bar is None:
            return
            
        if step_index >= len(self.STEPS):
            return
            
        # Calculate progress value (each step = ~16.67% for 6 steps)
        progress_value = int((step_index / len(self.STEPS)) * 100)
        text = self.STEPS[step_index]
        
        self.progress_bar.progress(progress_value, text=text)
        self.current_step = step_index
        
    def complete(self):
        """Complete the progress and clean up"""
        if self.progress_bar is None:
            return
            
        self.progress_bar.progress(100, text="✅ Documentation ready!")
        time.sleep(1)
        self.progress_bar.empty()
        
    def clear(self):
        """Clear the progress bar immediately"""
        if self.progress_bar:
            self.progress_bar.empty()
            self.progress_bar = None