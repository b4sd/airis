import speech_recognition as sr
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QScrollArea, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class SpeechRecognitionThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True  # To handle cancellation if needed

    def run(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        if not self._is_running:
            return

        try:
            with microphone as source:
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)

            recognized_text = recognizer.recognize_google(audio, language="vi-VN")
            self.update_signal.emit(recognized_text)
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError:
            print("Error connecting to the speech recognition service.")
        finally:
            self._is_running = False  # Ensure the thread marks itself as stopped