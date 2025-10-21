import streamlit as st
from typing import Optional, Tuple, List
from util.file_functions import FileHandler
from util.video_functions import VideoHandler


class VideoTrimmerHandler:
    """Handles all video trimming functionality and validation"""
    
    @staticmethod
    def parse_time_string(time_str: str) -> Optional[int]:
        """Parse MM:SS, M:SS, or H:MM:SS format to seconds"""
        try:
            time_str = time_str.strip()
            parts = time_str.split(':')
            
            if len(parts) == 2:  # MM:SS format
                minutes, seconds = int(parts[0]), int(parts[1])
                if 0 <= minutes and 0 <= seconds <= 59:
                    return minutes * 60 + seconds
            elif len(parts) == 3:  # H:MM:SS format
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                if 0 <= hours and 0 <= minutes <= 59 and 0 <= seconds <= 59:
                    return hours * 3600 + minutes * 60 + seconds
        except (ValueError, IndexError):
            pass
        return None
    
    @staticmethod
    def format_seconds_to_string(seconds: float) -> str:
        """Format seconds to MM:SS or H:MM:SS string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    @staticmethod
    def validate_time_inputs(start_time: Optional[int], end_time: Optional[int], 
                           video_duration: float) -> Tuple[bool, str, Optional[Tuple[float, float]]]:
        """
        Validate time inputs and return validation status, error message, and video segment
        
        Returns:
            Tuple[bool, str, Optional[Tuple[float, float]]]: 
            - validation_status: True if valid, False if invalid
            - error_message: Error message if invalid, empty string if valid
            - video_segment: (start_time, end_time) if valid, None if invalid
        """
        if start_time is None:
            return False, "⚠️ Invalid start time format. Please use MM:SS or H:MM:SS format (e.g., 1:30 or 0:01:30)", None
        
        if end_time is None:
            return False, "⚠️ Invalid end time format. Please use MM:SS or H:MM:SS format (e.g., 5:30 or 1:05:30)", None
        
        if start_time >= end_time:
            return False, "⚠️ Start time must be before end time", None
        
        if end_time > video_duration:
            return False, f"⚠️ End time exceeds video duration ({VideoTrimmerHandler.format_seconds_to_string(video_duration)})", None
        
        return True, "", (start_time, end_time)
    
    @staticmethod
    def render_time_inputs(video_duration: float) -> Tuple[str, str]:
        """Render the time input fields and return input values"""
        # Create two columns for start and end time inputs
        col1, col2 = st.columns(2)
        
        with col1:
            start_input = st.text_input(
                "Start time",
                value="0:00",
                placeholder="0:00 or 1:23:45",
                key="start_input",
                help="Enter time in MM:SS or H:MM:SS format"
            )
        
        with col2:
            # Default end time formatted as string
            default_end = VideoTrimmerHandler.format_seconds_to_string(video_duration)
            end_input = st.text_input(
                "End time",
                value=default_end,
                placeholder="5:30 or 1:23:45",
                key="end_input",
                help="Enter time in MM:SS or H:MM:SS format"
            )
        
        return start_input, end_input
    
    @staticmethod
    def display_validation_feedback(is_valid: bool, error_message: str, 
                                  start_time: int, end_time: int, video_duration: float):
        """Display validation feedback to the user"""
        if not is_valid:
            st.error(error_message)
        else:
            # Calculate segment duration
            segment_duration = end_time - start_time
            
            # Show success message with segment info
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ **Segment:** {VideoTrimmerHandler.format_seconds_to_string(start_time)} - {VideoTrimmerHandler.format_seconds_to_string(end_time)}")
            with col2:
                st.info(f"📹 **Duration:** {VideoTrimmerHandler.format_seconds_to_string(segment_duration)}")
    
    @staticmethod
    def render_video_trimmer(video_file, video_duration: float) -> Optional[Tuple[float, float]]:
        """
        Render the complete video trimmer interface
        
        Returns:
            Optional[Tuple[float, float]]: Video segment (start_time, end_time) if valid, None if invalid
        """
        with st.expander(f"Video trimmer tool - {video_file.name}", expanded=False, icon="✂️"):
            # Display original duration
            total_minutes = int(video_duration // 60)
            total_seconds = int(video_duration % 60)
            st.caption(f"Original duration: {total_minutes}:{total_seconds:02d}")
            
            # Render time input fields
            start_input, end_input = VideoTrimmerHandler.render_time_inputs(video_duration)
            
            # Parse inputs
            start_time = VideoTrimmerHandler.parse_time_string(start_input)
            end_time = VideoTrimmerHandler.parse_time_string(end_input)
            
            # Validate inputs
            is_valid, error_message, video_segment = VideoTrimmerHandler.validate_time_inputs(
                start_time, end_time, video_duration
            )
            
            # Display feedback
            VideoTrimmerHandler.display_validation_feedback(
                is_valid, error_message, start_time, end_time, video_duration
            )
            
            # Update session state
            st.session_state['video_segment_valid'] = is_valid
            
            return video_segment
    
    @staticmethod
    def handle_video_upload(uploaded_files: List, settings) -> Optional[Tuple[float, float]]:
        """
        Handle video file upload and trimming
        
        Args:
            uploaded_files: List of uploaded files
            settings: Settings object containing configuration
            
        Returns:
            Optional[Tuple[float, float]]: Video segment if valid, None if invalid
        """
        video_files = [f for f in uploaded_files if f.type == "video/mp4"]
        
        if not video_files:
            return None
        
        # Check for multiple videos
        if len(video_files) > 1:
            st.warning("Multiple videos detected. VisaCheck currently supports 1 video with extra content added. Please remove extra videos.", icon="❌")
            st.session_state['video_segment_valid'] = False
            return None
        
        # Reset validation state when only one video is present
        st.session_state['video_segment_valid'] = True
        video_file = video_files[0]
        
        try:
            # Save the video temporarily to get its duration
            video_file.seek(0)
            temp_video_path = FileHandler.save_file_locally(video_file, folder_path=settings.RAW_DATA_DIR)
            video_duration = VideoHandler.get_video_duration(temp_video_path)
            
            if video_duration:
                return VideoTrimmerHandler.render_video_trimmer(video_file, video_duration)
            else:
                st.error("Could not determine video duration. Please check if the video file is valid.")
                st.session_state['video_segment_valid'] = False
                return None
                
        except Exception as e:
            st.error(f"Error processing video file: {str(e)}")
            st.session_state['video_segment_valid'] = False
            print(f"Video processing error: {e}")
            return None
    
    @staticmethod
    def check_button_validation(uploaded_files: List) -> Tuple[bool, Optional[str]]:
        """
        Check if the Create Documentation button should be enabled
        
        Args:
            uploaded_files: List of uploaded files
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, help_message)
        """
        video_segment_valid = True
        help_message = None
        
        if uploaded_files:
            video_files = [f for f in uploaded_files if f.type == "video/mp4"]
            if len(video_files) > 1:
                # Multiple videos detected - disable button
                video_segment_valid = False
                help_message = "Please remove extra videos - only one video file is supported"
            elif video_files:
                # Single video - check if the segment is valid
                video_segment_valid = st.session_state.get('video_segment_valid', True)
                if not video_segment_valid:
                    help_message = "Please fix video segment validation errors before proceeding"
        
        return video_segment_valid, help_message