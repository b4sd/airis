import os
import pygame
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import sys
from google.cloud import texttospeech
from google.oauth2 import service_account
from PyQt5.QtCore import QThread, pyqtSignal
from misc.booksumary.summary_query import query_summary_page, query_summary_block
from LLM.getCompletion import getCompletion, get_completion_with_context
import time


class BookToSpeech(QThread):
    def __init__(self):
        super(BookToSpeech, self).__init__()
        
        # Initialize attributes
        # self.tts = tts
        self.book_audio_files = []
        self.current_index = 0
        self.is_paused = True
        self.pause_timestamp = 0
        self.is_saying = False
        self.chunks = []

        # Initialize pygame mixer and event system
        pygame.init()
        pygame.mixer.init()

        # Set custom event for detecting when audio ends
        self.audio_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.audio_end_event)

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

    def change_book(self, book_name):
        """Load all book audio files from the given book file."""
        try:
            book_path = "assets/book/" + book_name 
            sound_path = "sound/"

            # Clear the previous audio files in sound folder
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.init()
            for file in os.listdir(sound_path):
                os.remove(os.path.join(sound_path, file))

            # Load book text
            self.chunks = []
            for file in os.listdir(book_path):
                with open(os.path.join(book_path, file), "r", encoding="utf-8") as f:
                    self.chunks.append(f.read())

            # Convert each chunk to speech and save it to an audio file
            for i, chunk in enumerate(self.chunks):
                output_file = f"chunk_{i}.mp3"
                self.text_to_speech(chunk, AudioFolder=sound_path, output_file=output_file)
                self.book_audio_files.append(os.path.join(sound_path, output_file))        


            # Load the first audio file
            if self.book_audio_files:
                self.current_index = 0
                audio_file = self.book_audio_files[self.current_index]
                pygame.mixer.music.load(audio_file)

        except Exception as e:
            print(f"Error loading book: {e}")

    def resume(self):
        """Resume playing from the paused position."""
        try:
            if self.is_paused:
                self.is_paused = False
                # Load the paused audio file and play it from the paused position
                pygame.mixer.music.load(self.book_audio_files[self.current_index])
                pygame.mixer.music.play(start=max(0, self.pause_timestamp - 5))
        except Exception as e:
            print(f"Error resuming playback: {e}")

    def pause(self):
        """Pause playback and save the current timestamp."""
        try:
            if pygame.mixer.music.get_busy():
                self.is_paused = True
                self.pause_timestamp = pygame.mixer.music.get_pos() / 1000
                pygame.mixer.music.pause()
        except Exception as e:
            print(f"Error pausing playback: {e}")
    def play_next(self):
        """Play the next audio file in the book."""
        try:
            if self.current_index < len(self.book_audio_files) - 1:
                self.current_index += 1
                audio_file = self.book_audio_files[self.current_index]
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
            else:
                print("End of book reached.")
        except Exception as e:
            print(f"Error playing next audio: {e}")

    def say(self, text):
        try:
            """Pause book reading, convert text to speech, and play it immediately."""
            if pygame.mixer.music.get_busy():
                self.pause()  # Pause book reading

            output_file = "temp_say_audio.mp3"
            self.text_to_speech(text, AudioFolder="sound", output_file=output_file)

            pygame.mixer.music.load("sound/" + output_file)
            pygame.mixer.music.play()

            self.is_saying = True

            # while pygame.mixer.music.get_busy():
            #     pygame.time.wait(100)
        except Exception as e:
            print(f"Error saying text: {e}")

    def no_say(self):
        try:
            """Stop the current speech."""
            if pygame.mixer.music.get_busy() and self.is_saying:
                pygame.mixer.music.stop()
                # self.is_saying = False
                print("Stopped saying.")
        except Exception as e:
            print(f"Error saying text: {e}")

    def summary_page(self, book_title, start_page, end_page, start_chapter, end_chapter):
        try:
            self.say(query_summary_page(book_title, start_page, end_page, start_chapter, end_chapter))
        except Exception as e:
            print(f"Error saying text: {e}")

    def qna(self, question):
        try:
            self.say(getCompletion(userPrompt=question))
        except Exception as e:
            print(f"Error saying text: {e}")

    def qna_with_context(self, question):
        # Get 2 closest text blocks
        blocks = self.chunks[max(0, self.current_index - 1): self.current_index + 1]

        # Concat the blocks
        context = " ".join(blocks)

        try:
            self.say(get_completion_with_context(userPrompt=question, context=context))
        except Exception as e:
            print(f"Error saying text: {e}")


    def run(self):
        """Monitor playback and handle end events."""
        while True:
            for event in pygame.event.get():
                if event.type == self.audio_end_event:
                    if self.is_saying:
                        self.is_saying = False
                    else:
                        self.play_next()
            pygame.time.wait(1000)  # Avoid busy-waiting



# class ControllerThread(QThread):
#     # Signals to communicate with the BookToSpeech thread
#     change_book_signal = pyqtSignal(str)
#     pause_signal = pyqtSignal()
#     resume_signal = pyqtSignal()
#     say_signal = pyqtSignal(str)
#     next_signal = pyqtSignal()
#     summary_page_signal = pyqtSignal(str, int, int, int, int)
#     stop_say_signal = pyqtSignal()

#     def __init__(self):
#         super(ControllerThread, self).__init__()

#     def run(self):
#         while True:
#             command = input("Enter command (change, pause, resume, say, next): ").strip()
#             if command == "change":
#                 book_path = input("Enter book path: ")
#                 self.change_book_signal.emit(book_path)
#             elif command == "pause":
#                 self.pause_signal.emit()
#             elif command == "resume":
#                 self.resume_signal.emit()
#             elif command == "say":
#                 text = input("Enter text to say: ")
#                 self.say_signal.emit(text)
#             elif command == "next":
#                 self.next_signal.emit()
#             elif command == "sum":
#                 self.summary_page_signal.emit("book", 1, 1, 1, 1)
#             elif command == "stop":
#                 self.stop_say_signal.emit()
#             else:
#                 print("Invalid command.")

# if __name__ == "__main__":
#     # Add to the sys path to import the TTS processor
#     # sys.path.append("misc/piper")

#     # from TTS import TTSProcessor  # Assuming TTSProcessor is in 'misc/piper'

#     # Initialize PyQt application
#     app = QApplication(sys.argv)

#     # Initialize TTS processor
#     # tts_processor = TTSProcessor("Viet74K.txt")  # Provide the appropriate model file

#     # Create the BookToSpeech instance
#     book_to_speech_thread = BookToSpeech()

#     # Create the controller thread
#     controller_thread = ControllerThread()

#     # Connect controller signals to BookToSpeech methods
#     controller_thread.change_book_signal.connect(book_to_speech_thread.change_book)
#     controller_thread.pause_signal.connect(book_to_speech_thread.pause)
#     controller_thread.resume_signal.connect(book_to_speech_thread.resume)
#     controller_thread.next_signal.connect(book_to_speech_thread.play_next)
#     controller_thread.say_signal.connect(book_to_speech_thread.say)
#     controller_thread.summary_page_signal.connect(book_to_speech_thread.summary_page)
#     controller_thread.stop_say_signal.connect(book_to_speech_thread.no_say)

#     # Start the BookToSpeech thread
#     book_to_speech_thread.start()

#     # Start the Controller thread
#     controller_thread.start()

#     # Execute the PyQt application
#     sys.exit(app.exec_())
