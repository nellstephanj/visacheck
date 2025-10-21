import os
import moviepy.editor as mp
from io import BytesIO
from util.file_functions import FileHandler
import ffmpeg
from PIL import Image
import os
from config.settings import Settings

class VideoHandler:

    @staticmethod
    def get_video_duration(video_path):
        """Get the duration of a video in seconds"""
        try:
            video = mp.VideoFileClip(video_path)
            duration = video.duration
            video.close()  # Important: close to free memory
            return duration
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return None

    @staticmethod
    def extract_audio(video_path, settings: Settings, start_time=None, end_time=None):
        filename = FileHandler.extract_filename(video_path)
        
        # Create filename with segment info if provided
        if start_time is not None and end_time is not None:
            new_file_path = os.path.join(settings.AUDIO_DIR, f"{filename}_{start_time}_{end_time}.wav")
        else:
            new_file_path = os.path.join(settings.AUDIO_DIR, f"{filename}.wav")

        # Check if the file already exists
        if os.path.exists(new_file_path):
            print(f"Audio file already exists at {new_file_path}")
            return new_file_path

        try:
            video = mp.VideoFileClip(video_path)
            
            # Extract segment if start and end times are provided
            if start_time is not None and end_time is not None:
                video = video.subclip(start_time, end_time)
            
            video.audio.write_audiofile(new_file_path)
            print(f"Audio segment extracted to {new_file_path}")
            video.close()  # Important: close to free memory

            return new_file_path
        except Exception as e:
            print(f"Error extracting audio segment: {e}")
            return None
        
    @staticmethod
    def extract_frame(video_path, time_seconds, output_image_path):
        # Check if the output image file already exists
        if os.path.exists(output_image_path):
            print(f"Frame already exists at {output_image_path}")
            return output_image_path

        try:
            (
                ffmpeg
                .input(video_path, ss=time_seconds)
                .output(output_image_path, vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
            print(f"Frame extracted to {output_image_path}")
            return output_image_path
        except Exception as e:
            print(f"Error extracting frame at {time_seconds}s: {e}")
            return None