from PySide6.QtCore import QSize, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

from components.dialogs.multi_selection import MultiSelectionDialog
from core import AnkiExportThread, AppleNoteImport, AudioThread, WordLookupWorker
from views.layout import CentralWidget


class MainWindow(QMainWindow):
    user_definition_selection = Signal(list)
    user_word_selection = Signal(int)

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("Custom MainWindow")
        self.setObjectName("MainWindow")
        self.resize(1286, 985)
        self.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies([".AppleSystemUIFont"])
        self.setFont(font)

        self.submit_btn = QPushButton("Submit")
        self.qwidget = QWidget()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.submit_btn)
        self.qwidget.setLayout(self.v_layout)

        # self.setCentralWidget(self.qwidget)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

    def receive_audio_words(self, succeeded_words, errored_words):
        print(succeeded_words, errored_words)
        self.anki_thread = AnkiExportThread(
            succeeded_words, "English Words", "English Vocab"
        )
        self.anki_thread.start()
