import shutil
import streamlit as st
import time
from io import BytesIO
import re
from base64 import b64encode
from PIL import Image
import os
import pypdf

from config.settings import Settings
from util.azure_openai_functions import OpenAIHandler
from util.docx_functions import DocumentHandler
from util.video_functions import VideoHandler
from util.audio_functions import AudioHandler
from util.file_functions import FileHandler, ProcessedFile


class ManualHandler:
    @staticmethod
    def extract_text_from_file(file, openai_handler: OpenAIHandler, input_language_code, output_language_code, settings: Settings, video_segment=None):
        # Save file locally before processing it
        local_file_path = FileHandler.save_file_locally(file, folder_path=settings.RAW_DATA_DIR)
        print(f"Saved the uploaded file locally at: {local_file_path}")

        # Keep track of the video_path
        video_path = ""

        print(f"Processing {file.name}")

        if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            print("Detected a Word Document")
            extracted_text = DocumentHandler.extract_text_from_docx(file)
            file_type = "docx"
        elif file.type == "application/pdf":
            print("Detected a PDF Document")
            
            reader = pypdf.PdfReader(local_file_path)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += f"{page.extract_text()} \n"

            # Use BytesIO for uploading and processing PDFs
            #bytes_data = BytesIO(file.read())
            #extracted_text = openai_handler.interpret_pdf(bytes_data)
            file_type = "pdf"
        elif file.type == "text/plain":
            print("Detected a Text Document")
            extracted_text = openai_handler.extract_text_from_txt(file)
            file_type = "txt"
        elif file.type in ["image/jpeg", "image/png"]:
            print("Detected an Image")
            image_prompts = {
                "en": "What is shown in the screenshot? Give me as much as possible the exact content of the document, with the best possible description of each image in the screenshot.",
                "nl": "Wat staat er in de screenshot? Geef mij zoveel mogelijk de exacte inhoud van het document, met een zo goed mogelijke beschrijving van elke afbeelding in de screenshot."
            }
            image_prompt = image_prompts.get(output_language_code, image_prompts["nl"])

            extracted_text = openai_handler.interpret_image(local_file_path, image_prompt)
            file_type = "image"
        elif file.type == "video/mp4":
            print("Detected a Video")
            
            # Get progress tracker from session state
            progress_tracker = st.session_state.get('progress_tracker')
            
            # Step 1: Audio Extraction
            if progress_tracker:
                progress_tracker.update_step(0)
            
            # Extract Audio with segment selection if provided
            if video_segment:
                start_time, end_time = video_segment
                print(f"Processing video segment from {start_time}s to {end_time}s")
                audio_file_path = VideoHandler.extract_audio(local_file_path, settings, start_time, end_time)
            else:
                print("Processing entire video")
                audio_file_path = VideoHandler.extract_audio(local_file_path, settings)

            # Step 2: Audio Conversion
            if progress_tracker:
                progress_tracker.update_step(1)
            
            # Convert Audio to smaller format
            converted_audio_file_path = AudioHandler.convert_audio(audio_file_path, settings)

            # Step 3: Transcription
            if progress_tracker:
                progress_tracker.update_step(2)
            
            # Transcribe Audio through OpenAI API
            extracted_text = openai_handler.transcribe_audio(converted_audio_file_path, language=input_language_code)

            # Setting video_path
            video_path = local_file_path
            file_type = "video"
        else:
            extracted_text = None
            file_type = None
        
        print(extracted_text)
        # st.write(f"Extracted Text: {extracted_text}")

        result = ProcessedFile(
            file_name=file.name,
            extracted_text=extracted_text,
            video_path=video_path,
            file_type=file_type
        )

        return result
    
    @staticmethod
    def replace_placeholders_with_screenshots(manual_text, video_path, settings: Settings, video_segment=None):
        # Extract video name from the path
        video_name = os.path.splitext(os.path.basename(video_path))[0]

        # Create the screenshots directory
        screenshots_dir = os.path.join(settings.SCREENSHOT_DIR, video_name)
        os.makedirs(screenshots_dir, exist_ok=True)

        # Find all placeholders like <SCREENSHOT>x</SCREENSHOT>
        matches = re.findall(r'<SCREENSHOT>(\d+\.\d+)<\/SCREENSHOT>', manual_text)

        print(f"Screenshots will be taken at these timestamps (in seconds): {matches}")
        if video_segment:
            start_time, end_time = video_segment
            print(f"Video was trimmed from {start_time}s to {end_time}s - adjusting screenshot timestamps")

        image_paths = {}
        display_text = manual_text
        
        for match in matches:
            whisper_time_seconds = float(match)
            
            # Adjust timestamp if video was trimmed
            if video_segment:
                start_time, end_time = video_segment
                actual_video_time = whisper_time_seconds + start_time
                print(f"Adjusting screenshot time: {whisper_time_seconds}s (Whisper) -> {actual_video_time}s (original video)")
            else:
                actual_video_time = whisper_time_seconds
                
            image_path = os.path.join(screenshots_dir, f"screenshot_{whisper_time_seconds}.png")
            
            # Extract the frame from the video using the adjusted timestamp
            extracted_image_path = VideoHandler.extract_frame(video_path, actual_video_time, image_path)
            
            if extracted_image_path:
                # Store the image path
                image_paths[f'<SCREENSHOT>{whisper_time_seconds}</SCREENSHOT>'] = extracted_image_path
                
                # Convert the extracted image to base64 for displaying in Streamlit
                with open(extracted_image_path, "rb") as image_file:
                    encoded_string = b64encode(image_file.read()).decode('utf-8')
                    img_tag = f'<img src="data:image/png;base64,{encoded_string}" alt="Screenshot at {whisper_time_seconds} seconds">'

                    # Replace the placeholder with the image tag
                    display_text = display_text.replace(f'<SCREENSHOT>{whisper_time_seconds}</SCREENSHOT>', img_tag)
        
        return display_text, manual_text, image_paths
    
    @staticmethod
    def clear_local_folders(settings: Settings):
        """Remove the entire session directory and all its contents"""
        if os.path.exists(settings.SESSION_DIR):
            try:
                shutil.rmtree(settings.SESSION_DIR)
                print(f"Removed session directory: {settings.SESSION_DIR}")
            except Exception as e:
                print(f"Error removing session directory {settings.SESSION_DIR}: {e}")
        else:
            print(f"Session directory does not exist: {settings.SESSION_DIR}")

