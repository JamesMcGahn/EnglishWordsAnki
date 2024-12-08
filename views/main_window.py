import threading

from PySide6.QtCore import QSize, QThread
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QMainWindow

from apple_note_import import AppleNoteImport


class MainWindow(QMainWindow):
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
        self.import_words_from_apple_notes()

    def import_words_from_apple_notes(self):
        self.appleNoteThread = QThread(self)

        self.appleImport = AppleNoteImport("Words")
        self.appleImport.moveToThread(self.appleNoteThread)
        self.appleImport.result.connect(self.receive_words)

        self.appleNoteThread.start()
        self.appleImport.start_work.emit()

    def receive_words(self, words):
        print(words)
