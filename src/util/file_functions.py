import json
import os
from dataclasses import dataclass
import shutil

class FileHandler:
    @staticmethod
    def read_text_file(file_path, **kwargs):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

            return content.format(**kwargs)

    @staticmethod
    def write_json_file(data, output_path):
        with open(output_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Manual output saved to {output_path}")

    @staticmethod
    def write_text_file(content, output_path):
        with open(output_path, "w", encoding="utf-8") as text_file:
            text_file.write(content)
        print(f"Manual text saved to {output_path}")

    @staticmethod
    def save_file_locally(file, folder_path='raw'):
        # Ensure the target directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Define the full path for the new file
        file_path = os.path.join(folder_path, file.name)
        
        with open(file_path, 'wb') as f:
            f.write(file.read())
        
        return file_path
    
    @staticmethod
    def extract_filename(local_file_path):
        # Extract the base name (file name with extension)
        base_name = os.path.basename(local_file_path)
        
        # Split the base name to remove the file extension
        file_name, _ = os.path.splitext(base_name)
        
        return file_name


    
@dataclass
class ProcessedFile:
    file_name: str
    extracted_text: str
    video_path: str
    file_type: str