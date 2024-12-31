import os
import pygame
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication
import sys



class BookToSpeech(QThread):
    def __init__(self, tts):
        super(BookToSpeech, self).__init__()
        
        # Initialize attributes
        self.tts = tts
        self.book_audio_files = []
        self.current_index = 0
        self.is_paused = True
        self.pause_timestamp = 0
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

        # Initialize pygame mixer and event system
        pygame.init()
        pygame.mixer.init()

        # Set custom event for detecting when audio ends
        self.audio_end_event = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.audio_end_event)

    def change_book(self, book_path):
        """Load all book audio files from the given book file."""
        try:
            # Set path
            os.chdir(self.script_dir)

            # Release pygame mixer resources
            pygame.mixer.music.stop()

            if not os.path.exists(book_path):
                raise FileNotFoundError(f"Book file not found: {book_path}")

            self.book_audio_files = []
            self.current_index = 0

            with open(book_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Split into chuck of 1000 characters but keep the sentences intact
            sentences = content.split(".")
            chunks = []

            for sentence in sentences:
                if chunks and len(chunks[-1]) + len(sentence) < 1000:
                    chunks[-1] += sentence + "."
                else:
                    chunks.append(sentence)

            sentences = chunks

            # Clear the previous audio files in sound folder
            self.tts.remove_audio_files("sound")

            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if sentence:
                    output_file = f"sound/audio_{i}.wav"
                    self.tts.to_speech(sentence, output_file=output_file)
                    self.book_audio_files.append(output_file)

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

            output_file = "temp_say_audio.wav"
            self.tts.to_speech(text, output_file=output_file)

            pygame.mixer.music.load(output_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
        except Exception as e:
            print(f"Error saying text: {e}")

    def run(self):
        """Monitor playback and handle end events."""
        while True:
            for event in pygame.event.get():
                if event.type == self.audio_end_event:
                    # Handle the end of the current audio
                    self.play_next()
            pygame.time.wait(100)  # Avoid busy-waiting



class ControllerThread(QThread):
    # Signals to communicate with the BookToSpeech thread
    change_book_signal = pyqtSignal(str)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    say_signal = pyqtSignal(str)
    next_signal = pyqtSignal()

    def __init__(self):
        super(ControllerThread, self).__init__()

    def run(self):
        while True:
            command = input("Enter command (change, pause, resume, say, next): ").strip()
            if command == "change":
                book_path = input("Enter book path: ")
                self.change_book_signal.emit(book_path)
            elif command == "pause":
                self.pause_signal.emit()
            elif command == "resume":
                self.resume_signal.emit()
            elif command == "say":
                text = input("Enter text to say: ")
                self.say_signal.emit(text)
            elif command == "next":
                self.next_signal.emit()
            else:
                print("Invalid command.")

if __name__ == "__main__":
    # Add to the sys path to import the TTS processor
    sys.path.append("misc/piper")

    from TTS import TTSProcessor  # Assuming TTSProcessor is in 'misc/piper'

    # Initialize PyQt application
    app = QApplication(sys.argv)

    # Initialize TTS processor
    tts_processor = TTSProcessor("Viet74K.txt")  # Provide the appropriate model file

    # Create the BookToSpeech instance
    book_to_speech_thread = BookToSpeech(tts_processor)

    # Create the controller thread
    controller_thread = ControllerThread()

    # Connect controller signals to BookToSpeech methods
    controller_thread.change_book_signal.connect(book_to_speech_thread.change_book)
    controller_thread.pause_signal.connect(book_to_speech_thread.pause)
    controller_thread.resume_signal.connect(book_to_speech_thread.resume)
    controller_thread.next_signal.connect(book_to_speech_thread.play_next)
    controller_thread.say_signal.connect(book_to_speech_thread.say)

    # Start the BookToSpeech thread
    book_to_speech_thread.start()

    # Start the Controller thread
    controller_thread.start()

    # Execute the PyQt application
    sys.exit(app.exec_())
