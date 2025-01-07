from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QScrollArea, QFrame, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import sys
from utils import load_books_from_folder, get_most_similar_book
from CommandsMapping2 import command_mapping
from misc.booksumary.summary_query import query_summary_page, query_summary_block
from LLM.getCompletion import getCompletion
from books.getBooks import getBooks
from SpeakerThread import SpeakerThread
from SpeechRecognitionThread import SpeechRecognitionThread
from booktospeech import BookToSpeech

class BookReaderApp(QWidget):
    # Signals to communicate with the BookToSpeech thread
    change_book_signal = pyqtSignal(str)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    fast_forward_signal = pyqtSignal()
    rewind_signal = pyqtSignal()
    say_signal = pyqtSignal(str)
    next_signal = pyqtSignal()
    summary_page_signal = pyqtSignal(str, str, str, str, str)
    stop_say_signal = pyqtSignal()
    qna_signal = pyqtSignal(str)
    qna_with_context_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Book Reader")
        self.setGeometry(100, 100, 1600, 900)  # Increased window size for better view

        # Folder where books are located
        self.books_folder = "books"  # Path to the folder containing the books
        self.books = load_books_from_folder(self.books_folder)  # Load books from the folder

        self.current_book = None
        self.current_page = 0
        
        self.speech_thread = None
        self.init_ui()
        
        # self.speaker_thread = SpeakerThread()
        # self.speaker_thread.text_signal.connect(self.speaker_thread.handle_text_signal)
        # self.speaker_thread.stop_signal.connect(self.speaker_thread.stop_audio)
        # self.speaker_thread.pause_signal.connect(self.speaker_thread.pause_audio)
        # self.speaker_thread.continue_signal.connect(self.speaker_thread.unpause_audio)
        # self.speaker_thread.start()

        self.booktospeech_thread = BookToSpeech()

        # Connect controller signals to BookToSpeech methods
        self.change_book_signal.connect(self.booktospeech_thread.change_book)
        self.pause_signal.connect(self.booktospeech_thread.pause)
        self.resume_signal.connect(self.booktospeech_thread.resume)
        self.fast_forward_signal.connect(self.booktospeech_thread.fast_forward)
        self.rewind_signal.connect(self.booktospeech_thread.rewind)
        self.next_signal.connect(self.booktospeech_thread.play_next)
        self.say_signal.connect(self.booktospeech_thread.say)
        self.summary_page_signal.connect(self.booktospeech_thread.summary_page)
        self.stop_say_signal.connect(self.booktospeech_thread.no_say)
        self.qna_signal.connect(self.booktospeech_thread.qna)
        self.qna_with_context_signal.connect(self.booktospeech_thread.qna_with_context)

        # Start the BookToSpeech thread
        self.booktospeech_thread.start()

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
        # Key R to resume audio
        elif event.key() == Qt.Key_R:
            print("Key R detected, resuming audio...")
            self.resume_signal.emit()
        # Key P to pause audio
        elif event.key() == Qt.Key_P:
            print("Key P detected, pausing audio...")
            self.pause_signal.emit()
        # Key S to stop saying
        elif event.key() == Qt.Key_S:
            print("Key S detected, stopping speech...")
            self.stop_say_signal.emit()
        # # Key N to say next
        # elif event.key() == Qt.Key_N:
        #     print("Key N detected, saying next...")
        #     self.next_signal.emit()
        # Key Q to quit
        elif event.key() == Qt.Key_Q:
            print("Key Q detected, quitting...")
            self.close()
        # Key M to fast forward
        elif event.key() == Qt.Key_M:
            print("Key Right detected, fast forwarding...")
            self.fast_forward_signal.emit()
        # Key N to rewind
        elif event.key() == Qt.Key_N:
            print("Key Left detected, rewinding...")
            self.rewind_signal.emit()
        
    def start_speech_recognition(self):
        """Start speech recognition automatically shutting down after use."""
        if self.speech_thread is None or not self.speech_thread.isRunning():
            self.speech_thread = SpeechRecognitionThread()
            self.speech_thread.update_signal.connect(self.handle_recognized_text)
            self.speech_thread.finished.connect(self.cleanup_thread)  # Automatically clean up
            self.speech_thread.start()

    def cleanup_thread(self):
        """Cleanup after the thread finishes."""
        self.speech_thread = None

    def handle_recognized_text(self, text):
        """Handle the recognized speech"""
        print(f"Recognized speech: {text}")
        
        result = command_mapping(text)
        print("Command dịch được: ", result)

        speaker_script = ""
        
        if result['command'] in ['thoát chương trình', 'tắt chương trình', 'ngừng chương trình']:
            print("Thoát chương trình...")
            self.close()
        elif result['command'] == "đọc sách":
            book_title = result['parameters']['tên sách']
            book_name = get_most_similar_book(book_title)
            
            if book_name == "Not sure":
                print(f"Không tìm thấy sách {book_title}.")
            else:
                # content = get_book_content(book_name) # or redirect to the Thread Reading book + develope (store last read time into logs)
                print(f"Đang đọc sách {book_name}...")
                # Emit signal to change the book
                self.change_book_signal.emit(book_name)

        elif result['command'] == "tóm tắt":
            book_title = result['parameters']['tên sách']
            start_page = result['parameters']['trang bắt đầu']
            end_page = result['parameters']['trang kết thúc']
            start_chapter = result['parameters']['chương bắt đầu']
            end_chapter = result['parameters']['chương kết thúc']
            print(f"Tóm tắt sách {book_title} từ trang {start_page} đến trang {end_page}...")
            # summary = query_summary_page(book_title, start_page, end_page, start_chapter, end_chapter)
            # print(summary)
            # Emit signal to say the summary
            self.summary_page_signal.emit(book_title, start_page, end_page, start_chapter, end_chapter)
        elif result['command'] == "ghi chú":
            pass
        elif result['command'] == "hỏi đáp":
            question = result['parameters']['câu hỏi']
            print(f"Hỏi: {question}")
            # Emit signal to ask the question
            self.qna_with_context_signal.emit(question)

            # answer = getCompletion(userPrompt=question, promptStyle="QA")
            # print(f"Trả lời: {answer}")

        elif result['command'] == "get all books from database":
            books_lst = getBooks()
            text = "Đây là danh sách các sách trong cơ sở dữ liệu: " + ", ".join(books_lst)
        elif result['command'] == "tiếp tục":
            # Emit signal to resume the audio
            self.resume_signal.emit()
        elif result['command'] == "dừng đọc":
            # Emit signal to pause the audio
            self.pause_signal.emit()
        else:
            pass

        # self.speakText(text_to_say="Chào bạn, tôi là một trợ lý ảo!")
    
    # def speakText(self, text_to_say = "Chào bạn, tôi là một trợ lý ảo!"):
    #     """Start the Speaker thread"""
    #     self.speaker_thread.text_signal.emit(text_to_say)  # Send the text to be spoken

    # def pause_audio(self):
    #     """Pause the audio"""
    #     self.speaker_thread.pause_signal.emit()

    # def resume_audio(self):
    #     """Resume the audio"""
    #     self.speaker_thread.continue_signal.emit()

    # def stop_audio(self):
    #     """Stop the audio"""
    #     self.speaker_thread.stop_signal.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookReaderApp()
    window.show()
    print("App started, click 'Shift' to start speech recognition.")
    sys.exit(app.exec_())