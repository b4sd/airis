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
    # say_signal = pyqtSignal(str)
    def __init__(self):
        super(BookToSpeech, self).__init__()
        
        # Initialize attributes
        # self.tts = tts
        self.book_audio_files = []
        self.current_index = 0
        self.is_paused = True
        self.pause_timestamp = 0
        self.is_saying = False
        self.is_moving = False
        self.speaking_rate = 0.75
        self.audio_length = []
        self.chunks = []
        self.lastBookRead = {
            "book": None,
            "timeStamp": None,
            "block": None
        }
        self.say_timestamp = 0
        self.say_length = 0

        # Initialize pygame mixer and event system
        pygame.init()
        pygame.mixer.init()

        # Set custom event for detecting when audio ends
        self.audio_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.audio_end_event)

    def text_to_speech(self, text: str, AudioFolder="Audio", output_file="output.mp3", speaking_rate=1.0):
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
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speaking_rate)

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
            sound_path = "sound/book/" + book_name

            # Create the sound folder if it doesn't exist
            if not os.path.exists(sound_path):
                os.makedirs(sound_path)
            

            # Clear the previous audio files in sound folder
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.init()

            # Load book text
            self.chunks = []
            for file in os.listdir(book_path):
                with open(os.path.join(book_path, file), "r", encoding="utf-8") as f:
                    self.chunks.append(f.read())

            # Convert each chunk to speech and save it to an audio file
            for i, chunk in enumerate(self.chunks):
                output_file = f"chunk_{i}.mp3"
                # If the file not exists
                path_to_file = sound_path + "/" + output_file
                print(f"Path to file: {path_to_file}")
                if not os.path.exists(path_to_file):
                    self.text_to_speech(chunk, AudioFolder=sound_path, output_file=output_file, speaking_rate=self.speaking_rate)
                self.book_audio_files.append(os.path.join(sound_path, output_file))
                self.audio_length.append(pygame.mixer.Sound.get_length(pygame.mixer.Sound(os.path.join(sound_path, output_file))))

            # Load the first audio file
            if self.book_audio_files:
                self.current_index = 0
                self.pause_timestamp = 0
                self.is_paused = True
                self.is_saying = False
                audio_file = self.book_audio_files[self.current_index]
                pygame.mixer.music.load(audio_file)
                self._pause_mixer()
                self.lastBookRead["book"] = book_name
                self.lastBookRead["timeStamp"] = 0
                self.lastBookRead["block"] = 0

            print(f"Loaded {self.audio_length}.")

        except Exception as e:
            print(f"Error loading book: {e}")

    def _pause_mixer(self):
        """Process stuff"""
        if not self.is_saying:
            self.pause_timestamp += pygame.mixer.music.get_pos() / 1000
            self.lastBookRead["timeStamp"] = self.pause_timestamp
            pygame.mixer.music.pause()
        else: # saying (summerize, qna...)
            self.say_timestamp += pygame.mixer.music.get_pos() / 1000
            pygame.mixer.music.pause()

    def _play_mixer(self):
        """Process stuff"""
        # Load current audio file and play it from the paused position
        if not self.is_saying: # book reading
            pygame.mixer.music.load(self.book_audio_files[self.current_index])
            pygame.mixer.music.play(start=max(0, self.pause_timestamp))
        else: # saying (summerize, qna...)
            pygame.mixer.music.play(start=max(0, self.say_timestamp))


    def _fast_forward_mixer(self, delta=5):
        """Process stuff"""
        if not pygame.mixer.music.get_busy():
            return

        if self.is_saying:
            self.say_timestamp += delta
            if self.say_timestamp <= self.say_length:
                self._play_mixer()
            else:
                self.no_say()
            return
        self._pause_mixer()
        # Load current audio file and play it from the paused position
        self.pause_timestamp += delta
        if self.pause_timestamp <= self.audio_length[self.current_index]:
            self._play_mixer()
        else:
            if self.current_index < len(self.book_audio_files) - 1:
                self.pause_timestamp -= self.audio_length[self.current_index]
                self.current_index += 1
                self._play_mixer()

    def _rewind_mixer(self, delta=5):
        """Process stuff"""
        if not pygame.mixer.music.get_busy():
            return
        if self.is_saying:
            self.say_timestamp -= delta
            self.say_timestamp = max(0, self.say_timestamp)
            self._play_mixer()
            return
        self._pause_mixer()
        # Load current audio file and play it from the paused position
        self.pause_timestamp -= delta
        if self.pause_timestamp >= 0:
            self._play_mixer()
        else:
            if self.current_index > 0:
                self.current_index -= 1
                self.pause_timestamp += self.audio_length[self.current_index]
                self._play_mixer()
            else:
                self.pause_timestamp = 0
                self.current_index = 0
                self._play_mixer()

    def resume(self):
        """Resume playing from the paused position."""
        try:
            print("Resuming playback.")
            if self.is_paused:
                self.is_paused = False
                # Load the paused audio file and play it from the paused position
                self._play_mixer()
        except Exception as e:
            print(f"Error resuming playback: {e}")

    def pause(self):
        """Pause playback and save the current timestamp."""
        try:
            print("Pausing playback.")
            if pygame.mixer.music.get_busy():
                self.is_paused = True
                self._pause_mixer()
        except Exception as e:
            print(f"Error pausing playback: {e}")

    def fast_forward(self):
        """Fast forward the audio by 5 seconds."""
        try:
            print("Fast forwarding...")
            self._fast_forward_mixer(delta=5)

        except Exception as e:
            print(f"Error fast forwarding: {e}")
    
    def rewind(self):
        """Rewind the audio by 5 seconds."""
        try:
            print("Rewinding...")
            self._rewind_mixer(delta=5)
        except Exception as e:
            print(f"Error rewinding: {e}")

    def play_next(self):
        """Play the next audio file in the book."""
        try:
            print("Playing next audio...")
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
            print("Saying text...")
            """Pause book reading, convert text to speech, and play it immediately."""
            if pygame.mixer.music.get_busy():
                self.pause()  # Pause book reading

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.init()

            # Delete temp if exists
            if os.path.exists("sound/temp_say_audio.mp3"):
                os.remove("sound/temp_say_audio.mp3")

            output_file = "temp_say_audio.mp3"
            self.text_to_speech(text, AudioFolder="sound", output_file=output_file, speaking_rate=self.speaking_rate)

            self.say_timestamp = 0
            self.say_length = pygame.mixer.Sound.get_length(pygame.mixer.Sound("sound/" + output_file))

            pygame.mixer.music.load("sound/" + output_file)
            pygame.mixer.music.play()

            self.is_saying = True

        except Exception as e:
            print(f"Error saying text: {e}")

    def no_say(self):
        try:
            print("Stopping saying...")
            """Stop the current speech."""
            if pygame.mixer.music.get_busy() and self.is_saying:
                pygame.mixer.music.stop()
                # self.is_saying = False
                print("Stopped saying.")
        except Exception as e:
            print(f"Error saying text: {e}")

    def summary_page(self, book_title, start_page, end_page, start_chapter, end_chapter):
        print(f"book_title: {book_title}, start_page: {start_page}, end_page: {end_page}, start_chapter: {start_chapter}, end_chapter: {end_chapter}")
        try:
            if start_page == "" and end_page == "":
                # Get last 2 blocks id
                start_block = max(0, self.current_index - 1)
                end_block = self.current_index
                res = query_summary_block(book_title, start_block, end_block)
                self.say(res)
            else:
                res = query_summary_page(book_title, start_page, end_page, start_chapter, end_chapter)
                self.say(res)
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
                    print("Audio ended.")
                    print(f"Current index: {self.current_index}, is_paused: {self.is_paused}, is_saying: {self.is_saying}, is_moving: {self.is_moving}")
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
