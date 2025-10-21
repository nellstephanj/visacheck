import os
import subprocess
from util.file_functions import FileHandler
from config.settings import Settings
import ffmpeg

class AudioHandler:
    @staticmethod
    def convert_audio(input_audio_path, settings: Settings):
        filename = FileHandler.extract_filename(input_audio_path)
        new_file_path = os.path.join(settings.AUDIO_DIR, f"{filename}.ogg")

        # Check if the file already exists
        if os.path.exists(new_file_path):
            print(f"Converted audio file already exists at {new_file_path}")
            return new_file_path

        try:
            # Read the input file
            input_stream = ffmpeg.input(input_audio_path)

            # Apply the audio conversion settings
            output_stream = ffmpeg.output(
                input_stream, 
                new_file_path,
                acodec='libopus',
                ac=1,  # mono audio
                audio_bitrate='12k',
                application='voip',
                map_metadata='-1'  # remove metadata
            )

            # Run the ffmpeg command
            ffmpeg.run(output_stream, overwrite_output=True)

            print(f"Audio converted successfully to {new_file_path}")
            return new_file_path
        except ffmpeg.Error as e:
            print(f"Error converting audio: {e.stderr.decode() if e.stderr else str(e)}")
            return None
