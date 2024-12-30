import os
import pygame
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
import sys

class BookToSpeech(QThread):
    # Signals to communicate with the main thread
    change_book_signal = pyqtSignal(str)
    pause_reading_signal = pyqtSignal()
    resume_reading_signal = pyqtSignal()
    say_sentence_signal = pyqtSignal(str)

    def __init__(self, tts):
        super(BookToSpeech, self).__init__()
        
        # Initialize attributes
        self.tts = tts
        self.book_audio_files = []
        self.current_index = 0
        self.is_paused = False
        self.pause_timestamp = 0

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

    def change_book(self, book_path):
        """Load all book audio files from the given book file."""
        if not os.path.exists(book_path):
            raise FileNotFoundError(f"Book file not found: {book_path}")

        self.book_audio_files = []
        self.current_index = 0

        with open(book_path, 'r', encoding='utf-8') as file:
            content = file.read()

        sentences = content.split('.')  # Split into sentences

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:
                output_file = f"audio_{i}.wav"
                self.tts.to_speech(sentence, output_file=output_file)
                self.book_audio_files.append(output_file)

    def resume(self):
        """Resume playing from the paused position."""
        if self.is_paused:
            self.is_paused = False
            pygame.mixer.music.play(start=max(0, self.pause_timestamp - 5))

    def pause(self):
        """Pause playback and save the current timestamp."""
        if pygame.mixer.music.get_busy():
            self.is_paused = True
            self.pause_timestamp = pygame.mixer.music.get_pos() / 1000
            pygame.mixer.music.pause()

    def say(self, text):
        """Pause book reading, convert text to speech, and play it immediately."""
        self.pause()  # Pause book reading
        output_file = "temp_say_audio.wav"
        self.tts.to_speech(text, output_file=output_file)

        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.wait(100)

    def play_next(self):
        """Play the next audio file in the book."""
        if self.current_index < len(self.book_audio_files):
            audio_file = self.book_audio_files[self.current_index]
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            self.current_index += 1

            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)

class ControllerThread(QThread):
    input_command_signal = pyqtSignal(str)

    def __init__(self, book_to_speech):
        super(ControllerThread, self).__init__()
        self.book_to_speech = book_to_speech

    def run(self):
        while True:
            command = input("Enter command (change, pause, resume, say, next): ")
            self.input_command_signal.emit(command)

if __name__ == "__main__":
    # Add to the sys path to import the TTS processor
    sys.path.append("misc/piper")

    from TTS import TTSProcessor  # Assuming TTSProcessor is in 'misc/piper'

    # Initialize PyQt application
    app = QApplication(sys.argv)

    # Initialize TTS processor
    tts = TTSProcessor("Viet74K.txt")

    # Create the BookToSpeech instance
    book_to_speech = BookToSpeech(tts)

    # Create the controller thread
    controller = ControllerThread(book_to_speech)

    # Connect controller signals to BookToSpeech methods
    controller.input_command_signal.connect(lambda command: {
        "change": lambda: book_to_speech.change_book(input("Enter book path: ")),
        "pause": book_to_speech.pause,
        "resume": book_to_speech.resume,
        "say": lambda: book_to_speech.say(input("Enter text to say: ")),
        "next": book_to_speech.play_next
    }.get(command, lambda: print("Invalid command"))())

    # Start the threads
    controller.start()

    sys.exit(app.exec_())
