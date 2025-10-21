import openai
import os
import streamlit as st
from util.logging_functions import LoggingHandler
from util.file_functions import FileHandler
from util.azure_functions import AzureHandler
from util.session_manager import SessionManager
import base64
import json
from config.settings import Settings


class OpenAIHandler:
    def __init__(self, azure_handler: AzureHandler, logging_handler: LoggingHandler, settings: Settings):
        self.settings = settings
        self.logging_handler = logging_handler
        # Use cached OpenAI client for performance
        self.client = self._get_cached_openai_client()
        
        # Initialize message templates
        self.system_messages = {
            "en": "You are a helpful assistant and you always respond in English.",
            "nl": "Je bent een behulpzame assistent en je antwoordt altijd in het Nederlands."
        }
        self.rewrite_prompts = {
            "en": "Rewrite the following transcription into a step-by-step manual:\n\n{text}",
            "nl": "Herschrijf de volgende transcriptie in een stap-bij-stap handleiding:\n\n{text}"
        }
        self.model_name_gpt = os.getenv("MODEL_NAME_LLM")
        self.model_name_transcription = os.getenv("MODEL_NAME_TRANSCRIPTION")
    
    @staticmethod
    @st.cache_resource  # Cache the expensive OpenAI client creation
    def _get_cached_openai_client():
        """
        Create and cache OpenAI client. Uses API key directly from environment variables.
        Cached across all users since API configuration is the same.
        """
        # Get API key directly from environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
        
        if not azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
        
        print(f"Connecting to Azure OpenAI endpoint: {azure_endpoint}")
        print(f"Using API key: {api_key[:10]}...")
        
        try:
            return openai.AzureOpenAI(
                api_key=api_key,  
                api_version="2024-12-01-preview",
                azure_endpoint=azure_endpoint
            )
        except Exception as e:
            print(f"Error creating Azure OpenAI client: {e}")
            raise

    def transcribe_audio(self, audio_path, language):

        print("Transribe audio function is used")

        filename = FileHandler.extract_filename(audio_path)
        new_file_path_json = os.path.join(self.settings.JSON_DIR, f"{filename}.json")
        new_file_path_txt = os.path.join(self.settings.TEXT_DIR, f"{filename}.txt")
        new_file_path_txt_timestamps = os.path.join(self.settings.TEXT_DIR, f"{filename}_timestamps.txt")

        # Check if all three files already exist
        if (os.path.exists(new_file_path_json) and 
            os.path.exists(new_file_path_txt) and 
            os.path.exists(new_file_path_txt_timestamps)):
            print(f"All transcription files already exist for {filename}")
            
            # Read and return the existing output_text
            with open(new_file_path_txt_timestamps, 'r', encoding='utf-8') as f:
                return f.read()

        # If any file doesn't exist, proceed with transcription
        # Transcription request
        print(f"Using transcription model: {self.model_name_transcription}")
        print(f"Transcribing file: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model=self.model_name_transcription,
                    file=audio_file,
                    response_format="verbose_json",
                )
        except Exception as e:
            print(f"Error during transcription: {e}")
            print(f"Error type: {type(e)}")
            raise

        # Convert the transcription object to a dictionary
        transcription_dict = transcription.to_dict()

        # Log the duration from the API response
        if 'duration' in transcription_dict:
            duration_seconds = transcription_dict['duration']
            print(f"Audio duration: {duration_seconds} seconds")
            self.logging_handler.log_usage(model_name=self.model_name_transcription, log_usage_amount=duration_seconds, log_usage_unit= "Seconds")

        # Save the transcription as a JSON file
        with open(new_file_path_json, "w") as json_file:
            json.dump(transcription_dict, json_file, indent=4)
        
        print(f"Transcription saved to {new_file_path_json}")

        # Save the text to txt
        with open(new_file_path_txt, "w", encoding="utf-8") as text_file:
            text_file.write(transcription_dict['text'])

        # Generate output with timestamps and text
        segments = transcription_dict["segments"]
        output_text = ""
        for segment in segments:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            output_text += f"({start} - {end})\n"
            output_text += text + "\n\n"  # Blank line for separation between segments

        # Save the output_text to a file
        with open(new_file_path_txt_timestamps, 'w', encoding='utf-8') as f:
            f.write(output_text)

        return output_text


    # Function to interpret an image via the OpenAI API
    def interpret_image(self, image_path, image_prompt):

        print("Image analyst function is used - azure_openai_functions")
        # Getting the base64 string
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": image_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            try:
                response = self.client.chat.completions.create(
                    #model="gpt-4o",
                    model=self.model_name_gpt,
                    messages=messages,
                    max_tokens=3000,
                    temperature=0.3,
                    top_p=1.0,
                    n=1
                )

                # Log token usage
                if hasattr(response, 'usage'):
                    print(f"Prompt tokens used: {response.usage.prompt_tokens}")
                    print(f"Completion tokens used: {response.usage.completion_tokens}")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.prompt_tokens, log_usage_unit= "Input tokens")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.completion_tokens, log_usage_unit= "Output tokens")

                else:
                    print("Token usage information not available in the response.")

                return response.choices[0].message.content
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        
    
    def interpret_pdf(self, pdf_file):

        print("PDF interpreter is used - azure_openai_functions")
        
        # Encode the PDF file content to base64
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        print("Base64: " + base64_pdf)

        # Send the encoded PDF content to OpenAI for interpretation
        messages = [
            {"role": "user", 
             "content": 
             f"Extract the text from the PDF-document:\n\n<data:application/pdf;base64,{base64_pdf}>"}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name_gpt,
                messages=messages,
                max_tokens=3000,
                temperature=0.3,
                top_p=1.0,
                n=1
            )

            # Log token usage
            if hasattr(response, 'usage'):
                print(f"Prompt tokens used: {response.usage.prompt_tokens}")
                print(f"Completion tokens used: {response.usage.completion_tokens}")
                self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.prompt_tokens, log_usage_unit= "Input tokens")
                self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.completion_tokens, log_usage_unit= "Output tokens")

            else:
                print("Token usage information not available in the response.")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

        
    def extract_text_from_txt(self, txt_file):
        """Extracts text from a plain .txt file."""
        try:
            # Debug: Check if file content exists before processing
            txt_file.seek(0)  # Ensure we're at the start of the file
            raw_bytes = txt_file.read()
            
            # Debug: Print raw bytes for inspection
            print(f"File Raw Content (bytes): {raw_bytes}")
            
            # Decode the file content
            content = raw_bytes.decode("utf-8")
            print(f"Extracted Content from TXT: '{content}'")  # Debug statement
            
            # Additional checks and loggings
            if not content:
                print("Content is empty after reading and decoding.")
            
            return content
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""


    def process_multiple_files(self, text_folder, text_files, main_prompt_file, output_language):

        print("process_multiple_files function is used")

        messages = [{"role": "system", "content": self.system_messages.get(output_language, self.system_messages["nl"])}]

        for text_file in text_files:
            file_path = os.path.join(text_folder, text_file)
            text_content = FileHandler.read_text_file(file_path)
            messages.append({"role": "user", "content": text_content})

        main_prompt = FileHandler.read_text_file(main_prompt_file)
        messages.append({"role": "user", "content": main_prompt})

        response = self.client.chat.completions.create(
            model=self.model_name_gpt,
            messages=messages,
            max_tokens=16384,
            temperature=0.3,
            top_p=1.0,
            n=1,
        )

        # Print token usage
        if hasattr(response, 'usage'):
            print(f"Prompt tokens used: {response.usage.prompt_tokens}")
            print(f"Completion tokens used: {response.usage.completion_tokens}")
            self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.prompt_tokens, log_usage_unit= "Input tokens")
            self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=response.usage.completion_tokens, log_usage_unit= "Output tokens")

        else:
            print("Token usage information not available in the response.")

        return response.choices[0].message.content, response.to_dict()
    

    def create_manual_based_on_multiple_files(self, processed_files, main_prompt_file, language_output):

        print("create_manual_based_on_multiple_files is used")

        messages = [{"role": "system", "content": self.system_messages.get(language_output, self.system_messages["nl"])}]

        for pf in processed_files:
            messages.append({"role": "user", "content": pf.extracted_text})

        main_prompt = FileHandler.read_text_file(main_prompt_file, language_output=language_output)
        messages.append({"role": "user", "content": main_prompt})

        print("Starting request to Azure OpenAI")
        # print("Messages being sent:", messages)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name_gpt,
                #model="genaitrainingtool_gpt4o",
                messages=messages,
                max_tokens=16384,
                temperature=0.3,
                top_p=1.0,
                n=1,
                stream=True,
                stream_options= {"include_usage": True}
            ) # type: ignore

            # print("API Response:", response)
            full_response = ""
            usage_info = None
            
            for chunk in response:
                # Check if this chunk contains usage information (final chunk) & Log usage
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    usage_info = chunk.usage
                    print(f"Token Usage: {usage_info.prompt_tokens}")
                    print(f"Completion: {usage_info.completion_tokens}")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=usage_info.prompt_tokens, log_usage_unit= "Input tokens")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=usage_info.completion_tokens, log_usage_unit= "Output tokens")
                    
                    SessionManager.update_activity()
                    continue  # Skip processing this chunk as content since it's the usage chunk
                
                # Process content chunks
                if not chunk.choices == []:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content
            
            return full_response
        except Exception as e:
            print(f"An error occurred while creating manual based on multiple files: {e}")
            return None

    def chat_with_gpt(self, chat_history):
        """
        Chat with GPT-4o using the chat history.
        Streams the response back to the UI.
        """
        print("chat_with_gpt function is used")
        
        try:
            # Prepare messages for the API
            messages = []
            for message in chat_history:
                messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            SessionManager.update_activity()
            response = self.client.chat.completions.create(
                model=self.model_name_gpt,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                top_p=1.0,
                n=1,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            full_response = ""
            usage_info = None

            for chunk in response:
                # Check if this chunk contains usage information (final chunk)
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    usage_info = chunk.usage
                    print(f"Token Usage: {usage_info.prompt_tokens}")
                    print(f"Completion: {usage_info.completion_tokens}")
                    self.logging_handler.log_usage(
                        model_name=self.model_name_gpt, 
                        log_usage_amount=usage_info.prompt_tokens, 
                        log_usage_unit="Input tokens"
                    )
                    self.logging_handler.log_usage(
                        model_name=self.model_name_gpt, 
                        log_usage_amount=usage_info.completion_tokens, 
                        log_usage_unit="Output tokens"
                    )
                    
                    SessionManager.update_activity()
                    continue  # Skip processing this chunk as content since it's the usage chunk
                
                # Process content chunks
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            return full_response
        except Exception as e:
            print(f"An error occurred during chat: {e}")
            yield f"Sorry, I encountered an error: {str(e)}"
    
      
    def rewrite_to_manual(self, extracted_text, output_language):

        print("rewrite_to_manual function is used - azure_openai_functions")

        try:
            prompt_template = self.rewrite_prompts.get(output_language, self.rewrite_prompts["nl"])
            SessionManager.update_activity()
            response = self.client.chat.completions.create(
                #model="gpt-4o",
                model=self.model_name_gpt,
                messages=[
                    {"role": "user", 
                     "content": prompt_template.format(text=extracted_text)}
                ],
                max_tokens=16384,
                temperature=0.3,
                top_p=1.0,
                n=1,
                stream=True,  # Enable streaming
                stream_options= {"include_usage": True} #Include usage in last chunk 
            ) # type: ignore
            
            full_response = ""
            usage_info = None

            for chunk in response:
                # Check if this chunk contains usage information (final chunk)
                if hasattr(chunk, 'usage') and chunk.usage is not None:
                    usage_info = chunk.usage
                    print(f"Token Usage: {usage_info.prompt_tokens}")
                    print(f"Completion: {usage_info.completion_tokens}")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=usage_info.prompt_tokens, log_usage_unit= "Input tokens")
                    self.logging_handler.log_usage(model_name=self.model_name_gpt, log_usage_amount=usage_info.completion_tokens, log_usage_unit= "Output tokens")
                    
                    SessionManager.update_activity()
                    continue  # Skip processing this chunk as content since it's the usage chunk
                
                # Process content chunks
                if not chunk.choices == []:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content
            
            return full_response
        except Exception as e:
            print(f"An error occurred while creating manual based on multiple files: {e}")
            return None