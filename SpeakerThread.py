import pygame
import os
from google.cloud import texttospeech
from google.oauth2 import service_account
from PyQt5.QtCore import QThread, pyqtSignal
import time

class SpeakerThread(QThread):
    text_signal = pyqtSignal(str)
    pause_signal = pyqtSignal()
    continue_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_paused = False
        self.is_playing = False
        self.current_audio_file = None
        self.is_running = True  # To control the loop in run()
        self.is_processing = False  # Flag to prevent re-entrant processing

        # Initialize pygame mixer here to avoid the "not initialized" error
        pygame.mixer.init()

    def run(self):
        """Thread run loop to listen for signals and process actions."""
        print("Speaker thread running. Waiting for signals...")

    def handle_text_signal(self, text: str):
        """Handles the text signal and starts TTS."""
        if self.is_processing:
            print("Already processing, skipping the new request.")
            return
        
        print("Received signal to speak:", text)
        self.is_processing = True  # Set flag to prevent re-entrant processing
        
        try:
            self.text_to_speech(text)
            self.play_audio(self.current_audio_file)
        finally:
            self.is_processing = False  # Reset flag after processing

    def text_to_speech(self, text: str, AudioFolder="Audio", output_file="output.mp3"):
        """Converts text to speech and saves it to an audio file."""
        credentials = service_account.Credentials.from_service_account_file("vision_key.json")
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Configure text-to-speech input
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Configure voice (Vietnamese)
        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        # Configure audio output
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

        # Send the request and save the audio file
        response = client.synthesize_speech(
            request={"input": synthesis_input, "voice": voice, "audio_config": audio_config}
        )
        
        if not os.path.exists(AudioFolder):
            os.makedirs(AudioFolder)
        
        # Ensure that the file is overwritten only if needed
        self.current_audio_file = os.path.join(AudioFolder, output_file)

        # Wait until pygame is done with the old file
        if os.path.exists(self.current_audio_file):
            # Check if audio is still playing
            if pygame.mixer.music.get_busy():
                print("Audio is still playing, waiting...")
                pygame.mixer.music.stop()  # Stop the music if it's playing
            
            # Wait a bit before trying to delete the file
            time.sleep(1)  # Allow time for audio to stop
            
            try:
                os.remove(self.current_audio_file)  # Remove the old file before writing again
            except PermissionError:
                print(f"Unable to remove the file {self.current_audio_file} because it is in use.")
                return  # Skip writing the new file

        # Now save the new audio content
        with open(self.current_audio_file, "wb") as out:
            out.write(response.audio_content)

    def play_audio(self, file_path: str):
        """Play audio using pygame."""
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        self.is_playing = True
        print("Playing audio...")

    def pause_audio(self):
        """Pause the currently playing audio."""
        try:
            pygame.mixer.music.pause()
            print("Audio paused.")
        except Exception as e:
            print(f"Failed to pause audio: {str(e)}")

    def unpause_audio(self):
        """Resume the currently paused audio."""
        try:
            pygame.mixer.music.unpause()
            print("Audio resumed.")
        except Exception as e:
            print(f"Failed to resume audio: {str(e)}")

    def stop_audio(self):
        """Stop the currently playing audio."""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            print("Audio stopped.")
        except Exception as e:
            print(f"Failed to stop audio: {str(e)}")

    def stop(self):
        """Stop the thread's execution."""
        self.is_running = False
        self.quit()
