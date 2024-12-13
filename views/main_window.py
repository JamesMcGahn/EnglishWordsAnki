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

        self.submit_btn.clicked.connect(self.import_words_from_apple_notes)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

    def import_words_from_apple_notes(self):
        self.appleNoteThread = QThread()

        self.appleImport = AppleNoteImport("Words")
        self.appleImport.moveToThread(self.appleNoteThread)
        self.appleImport.result.connect(self.receive_words)

        self.appleNoteThread.start()
        self.appleImport.start_work.emit()

    def receive_words(self, words):
        print(words)
        # self.word_lookup_thread = QThread()
        self.word_lookup = WordLookupWorker(["bird", "cat"])
        self.word_lookup.multi_definitions.connect(self.select_definitions)
        self.word_lookup.multi_words.connect(self.select_word)
        self.user_definition_selection.connect(
            self.word_lookup.get_user_definition_selection
        )
        self.user_word_selection.connect(self.word_lookup.get_user_word_selection)
        self.word_lookup.defined_words.connect(self.receive_defined_words)
        self.word_lookup.skipped_words.connect(self.receive_skipped_words)
        self.word_lookup.start()

    def select_word(self, words):
        print("********", words)
        choices = [
            f'{word["word"]} - { word["partOfSpeech"]} - {word["meaning"]}'
            for word in words
        ]

        self.multi_dialog = MultiSelectionDialog(
            choices, "Found Multiple Words", "Choose a Word", True
        )
        self.multi_dialog.md_multi_def_signal.connect(self.receive_word_selection)
        self.multi_dialog.exec()

    def select_definitions(self, definitions):
        print("********", definitions)
        choices = [
            f"{definition.partOfSpeech} - {definition.definition}"
            for definition in definitions
        ]
        self.multi_dialog = MultiSelectionDialog(
            choices, "Found Multiple Definitions", "Choose a Defintion", False
        )
        self.multi_dialog.md_multi_def_signal.connect(self.receive_definition_selection)
        self.multi_dialog.exec()

    def receive_word_selection(self, choice):
        print(choice)
        self.user_word_selection.emit(choice[0])

    def receive_definition_selection(self, choices):
        print(choices)
        self.user_definition_selection.emit(choices)

    def receive_defined_words(self, words):
        print("defined words", words)
        self.audio_thread = AudioThread(words, "./")
        self.audio_thread.succeeded_errored_words.connect(self.receive_audio_words)
        self.audio_thread.start()

    def receive_skipped_words(self, words):
        print("skipped words", words)

    def receive_audio_words(self, succeeded_words, errored_words):
        print(succeeded_words, errored_words)
        self.anki_thread = AnkiExportThread(
            succeeded_words, "English Words", "English Vocab"
        )
        self.anki_thread.start()
