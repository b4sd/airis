from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QScrollArea, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
import speech_recognition as sr
from utils import load_books_from_folder, get_most_similar_book
from CommandsMapping2 import command_mapping
from misc.booksumary.summary_query import query_summary
from LLM.getCompletion import getCompletion

class SpeechRecognitionThread(QThread):
    update_signal = pyqtSignal(str)

    def run(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        try:
            with microphone as source:
                # recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)

            recognized_text = recognizer.recognize_google(audio, language="vi-VN")
            self.update_signal.emit(recognized_text)
        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError:
            print("Error connecting to the speech recognition service.")

class BookReaderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Book Reader")
        self.setGeometry(100, 100, 1600, 900)  # Increased window size for better view

        # self.setWindowFlags(Qt.FramelessWindowHint)

        # Folder where books are located
        self.books_folder = "books"  # Path to the folder containing the books
        self.books = load_books_from_folder(self.books_folder)  # Load books from the folder

        self.current_book = None
        self.current_page = 0
        
        self.speech_thread = SpeechRecognitionThread()
        # self.speech_thread.update_signal.connect(self.open_book)
        self.speech_thread.update_signal.connect(self.handle_recognized_text)
        self.init_ui()

    def init_ui(self):
        # Set the background color to white
        self.setStyleSheet("background-color: white;")

        # Create the main layout (horizontal layout with sidebar)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)  # Ensure no spacing between the sidebar and content
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(0, 25, 0, 25)

        # Set alignment of the layout to align all widgets at the top
        sidebar_layout.setAlignment(Qt.AlignTop)

        # Home Button with an image
        home_button = QPushButton("Home", self)
        home_button.setStyleSheet("""
        QPushButton {
            background-color: #E4E4E3;
            color: black;
            font-family: 'Verdana';
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 10px;
        }
        QPushButton:hover {
            background-color: #A09D9E;
        }
        QPushButton:pressed {
            background-color: #424141;
        }
        """)
        home_button.clicked.connect(self.go_to_home)
        sidebar_layout.addWidget(home_button)

        # Settings Button with an image
        settings_button = QPushButton("Settings", self)
        settings_button.setStyleSheet("""
        QPushButton {
            background-color: #E4E4E3;
            color: black;
            font-family: 'Verdana';
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 10px;
        }
        QPushButton:hover {
            background-color: #A09D9E;
        }
        QPushButton:pressed {
            background-color: #424141;
        }
        """)
        sidebar_layout.addWidget(settings_button)

        # Spacer to push the "Quit" button to the bottom
        sidebar_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Quit Button
        quit_button = QPushButton("Quit", self)
        quit_button.setStyleSheet("""
        QPushButton {
            background-color: #E4E4E3;
            color: black;
            font-family: 'Verdana';
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 10px;
        }
        QPushButton:hover {
            background-color: #A09D9E;
        }
        QPushButton:pressed {
            background-color: #424141;
        }
        """)
        quit_button.clicked.connect(self.close)
        sidebar_layout.addWidget(quit_button)

        # Set the sidebar width and add it to the main layout
        sidebar_widget = QWidget(self)
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(200)  # Fixed width for the sidebar

        # Set auto-fill background for the widget
        sidebar_widget.setAutoFillBackground(True)

        # Apply the stylesheet to sidebar_widget
        sidebar_widget.setStyleSheet("""
        QWidget {
            background-color: #E4E4E3;  /* Light gray background color */
            border-radius: 5px;
        }
        """)

        # Right content area (book list, pages)
        self.stacked_widget = QStackedWidget(self)
        self.book_list_layout = QHBoxLayout()
        self.book_list_layout.setSpacing(15)

        for idx, (book_title, book_data) in enumerate(self.books.items()):
            book_layout = QVBoxLayout()
            book_layout.setContentsMargins(0, 0, 0, 0)

            cover_button = QPushButton(self)
            cover_button.setStyleSheet("background-color: transparent; border: none;")
            cover_pixmap = QPixmap(book_data["cover"]).scaled(200, 300, Qt.KeepAspectRatio)
            cover_button.setIcon(QIcon(cover_pixmap))
            cover_button.setIconSize(cover_pixmap.size())

            title_label = QLabel(book_title, self)
            title_label.setStyleSheet("""
                font-family: 'Comic Sans MS';
                font-size: 14px;
                color: black;
                margin-top: 0px;
            """)
            title_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

            book_layout.addWidget(cover_button)
            book_layout.addWidget(title_label)

            self.book_list_layout.addLayout(book_layout)
            cover_button.clicked.connect(lambda checked, title=book_title: self.open_book(title))

        self.main_screen = QWidget(self)
        self.main_screen.setLayout(self.book_list_layout)
        self.stacked_widget.addWidget(self.main_screen)

        # Book content screen layout
        self.page_label = QLabel(self)
        self.page_label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        page_frame = QFrame(self)
        page_frame.setStyleSheet("background-color: white; padding: 0px; border: none;")

        scroll_area = QScrollArea(self)
        scroll_area.setWidget(self.page_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable vertical scroll bar
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        page_frame.setLayout(QVBoxLayout())
        page_frame.layout().addWidget(scroll_area)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous", self)
        self.prev_button.setStyleSheet("""
                                       QPushButton {
            background-color: #E4E4E3;
            color: black;
            font-family: 'Verdana';
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 10px;
        }
        QPushButton:hover {
            background-color: #A09D9E;
        }
        QPushButton:pressed {
            background-color: #424141;
        }
        """)
        self.prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next", self)
        self.next_button.setStyleSheet("""
                                       QPushButton {
            background-color: #E4E4E3;
            color: black;
            font-family: 'Verdana';
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 10px 10px;
        }
        QPushButton:hover {
            background-color: #A09D9E;
        }
        QPushButton:pressed {
            background-color: #424141;
        }
        """)
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)

        self.book_content_layout = QVBoxLayout()
        self.book_content_layout.addWidget(page_frame)
        self.book_content_layout.addLayout(nav_layout)

        self.book_content_screen = QWidget(self)
        self.book_content_screen.setLayout(self.book_content_layout)

        self.stacked_widget.addWidget(self.book_content_screen)

        # Add the sidebar and content area to the main layout
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.stacked_widget)

        self.setLayout(main_layout)

    def go_to_home(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)
        self.current_book = None

    def open_book(self, book_title):
        self.current_book = self.books[book_title]
        self.current_page = 0
        self.update_page()
        self.stacked_widget.setCurrentWidget(self.book_content_screen)

    def update_page(self):
        if self.current_book:
            page_image_path = self.current_book["content"][self.current_page]
            pixmap = QPixmap(page_image_path)
            self.page_label.setPixmap(pixmap)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        if self.current_page < len(self.current_book["content"]) - 1:
            self.current_page += 1
            self.update_page()

    def keyPressEvent(self, event):
        """Detect spacebar press to trigger the speech recognition"""
        if event.key() == Qt.Key_Shift:
            self.start_speech_recognition()
        if event.key() == Qt.Key_S and self.current_book != None:
            pass # stop speech 

    def start_speech_recognition(self):
        """Start the speech recognition thread"""
        if not self.speech_thread.isRunning():
            self.speech_thread.start()

    def handle_recognized_text(self, text):
        """Handle the recognized speech"""
        print(f"Recognized speech: {text}")
        
        result = command_mapping(text)
        print("Command dịch được: ", result)

        if result['command'] in ['thoát chương trình', 'tắt chương trình', 'ngừng chương trình']:
            print("Thoát chương trình...")
            self.close()
        elif result['command'] == "đọc sách":
            book_title = result['parameters']['tên sách']
            book_name = get_most_similar_book(book_title)
            print(f"Đang đọc sách {book_name}...")
        elif result['command'] == "tóm tắt":
            book_title = result['parameters']['tên sách']
            start_page = result['parameters']['trang bắt đầu']
            end_page = result['parameters']['trang kết thúc']
            start_chapter = result['parameters']['chương bắt đầu']
            end_chapter = result['parameters']['chương kết thúc']
            print(f"Tóm tắt sách {book_title} từ trang {start_page} đến trang {end_page}...")
            summary = query_summary(book_title, start_page, end_page, start_chapter, end_chapter)
            print(summary)
        elif result['command'] == "ghi chú":
            pass
        elif result['command'] == "hỏi đáp":
            question = result['parameters']['câu hỏi']
            print(f"Hỏi: {question}")
            answer = getCompletion(userPrompt=question, promptStyle="QA")
            print(f"Trả lời: {answer}")
        # elif result['command'] == "tiếp tục":
        #     pass
        # elif result['command'] == "dừng đọc":
        #     pass
        else:
            pass

        # # Convert the response to speech
        # pause_audio()
        # text_to_speech(response, "respond.mp3")
        # play_audio("respond.mp3")
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookReaderApp()
    window.show()
    print("App started, click 'Shift' to start speech recognition.")
    sys.exit(app.exec_())