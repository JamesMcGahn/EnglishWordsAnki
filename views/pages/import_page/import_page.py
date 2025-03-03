import uuid

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

from base import QWidgetBase
from components.helpers import WidgetFactory
from core.apple_note_import import AppleNoteImport
from models import Status, WordModel, WordsModel


class ImportPage(QWidgetBase):
    add_word_to_model = Signal(WordModel)
    save_words_to_model = Signal()
    to_define_word = Signal(str, Status)
    start_defining_words = Signal(int)
    delete_words_model = Signal(list)

    def __init__(self):
        super().__init__()
        self.word_list = []
        word_set_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()

        self.apple_note_name = None
        self.apple_note_verified = False

        top_btn_h_layout = QHBoxLayout()
        self.import_btn = QPushButton("Import")
        self.import_btn.setMinimumWidth(200)
        hspacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_btn_h_layout.addItem(hspacer)
        top_btn_h_layout.addWidget(self.import_btn)
        word_set_layout.addLayout(top_btn_h_layout)

        self.arrow_up = QPushButton("")
        self.arrow_down = QPushButton("")
        self.arrow_down.setCursor(Qt.PointingHandCursor)
        self.arrow_up.setCursor(Qt.PointingHandCursor)
        WidgetFactory.create_icon(
            self.arrow_up,
            ":/images/up_arrow_off_b.png",
            49,
            20,
            False,
            ":/images/up_arrow_on.png",
            False,
        )
        WidgetFactory.create_icon(
            self.arrow_down,
            ":/images/down_arrow_off_b.png",
            49,
            20,
            False,
            ":/images/down_arrow_on.png",
            False,
        )
        # Nav Buttons
        nav_box = QVBoxLayout()
        nav_box.addWidget(self.arrow_up)
        nav_box.addWidget(self.arrow_down)

        h_layout.addLayout(nav_box)
        word_set_layout.addLayout(h_layout)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        self.start_define_btn = QPushButton("Define Selected Words")
        self.delete_words_btn = QPushButton("Delete Selected Words")
        bottom_btn_h_layout = QHBoxLayout()
        bottom_btn_h_layout.addWidget(self.start_define_btn)
        bottom_btn_h_layout.addWidget(self.delete_words_btn)
        word_set_layout.addLayout(bottom_btn_h_layout)

        h_layout.addWidget(self.list_widget)

        self.wordsModel = WordsModel()
        # SLOTS / SIGNALS
        self.import_btn.clicked.connect(self.import_words_from_apple_notes)
        self.arrow_up.clicked.connect(self.navigate_up)
        self.arrow_down.clicked.connect(self.navigate_down)
        self.add_word_to_model.connect(self.wordsModel.add_word)
        self.wordsModel.word_added.connect(self.add_word)
        self.save_words_to_model.connect(self.wordsModel.save_words)
        self.start_define_btn.clicked.connect(self.start_define_words)
        self.to_define_word.connect(self.wordsModel.update_status)
        self.delete_words_model.connect(self.wordsModel.delete_words)
        self.delete_words_btn.clicked.connect(self.delete_words)

        for word in self.wordsModel.undefined_words:
            self.add_word(word)

    def navigate_up(self):
        """
        Moves the selection up in the rule set list.
        If at the top, it moves selection to the last item in the list

        Returns:
            None: This function does not return a value.
        """
        if self.list_widget.currentRow() > 0:
            self.list_widget.setCurrentRow(self.list_widget.currentRow() - 1)
        else:
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def navigate_down(self):
        """
        Moves the selection down in the rule set list.
        If at the bottom, it moves selection to the first item in the list

        Returns:
            None: This function does not return a value.
        """
        if self.list_widget.currentRow() != self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(self.list_widget.currentRow() + 1)
        else:
            self.list_widget.setCurrentRow(0)

    @Slot(WordModel)
    def add_word(self, word: WordModel) -> None:
        """
        Slot for adding a rule set to the list of rules
        Args:
            word (object): A word to be added to the list.
                The word should be a dictionary with the following structure:
                "guid": A unique identifier for the word,
                "word": the word,

        Returns:
            None: This function does not return a value.

        """

        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.list_widget.addItem(list_item)
        self.word_list.append(word)
        if self.list_widget.count() == 1:
            self.list_widget.setCurrentRow(0)

    def import_words_from_apple_notes(self):
        print(self.apple_note_name, self.apple_note_verified)
        if not self.apple_note_name:
            self.log_with_toast(
                "Apple Note Name Not Set",
                "Please enter the Apple note name on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        if not self.apple_note_verified:
            self.log_with_toast(
                "Apple Note Name Not Verified",
                "Please verified the Apple note name on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        self.appleNoteThread = QThread()
        self.appleImport = AppleNoteImport(self.apple_note_name)
        self.appleImport.moveToThread(self.appleNoteThread)
        self.appleImport.result.connect(self.receive_words)
        self.appleImport.finished.connect(self.appleImport.deleteLater)
        self.appleImport.finished.connect(self.appleNoteThread.quit)
        self.appleNoteThread.finished.connect(self.appleNoteThread.deleteLater)
        self.appleNoteThread.started.connect(self.appleImport.do_work)
        self.appleNoteThread.start()

    def receive_words(self, words):
        for word in words:
            new_word = WordModel(
                Status.ADDED, str(uuid.uuid4()), word, "", "", "", "", ""
            )
            self.add_word_to_model.emit(new_word)
        self.save_words_to_model.emit()
        self.log_with_toast(
            "Imported Words From Apple Note",
            "Words have been imported from Apple Note.",
            "INFO",
            "SUCCESS",
            parent=self,
        )

    def start_define_words(self):
        selected_words = self.list_widget.selectedItems()

        for word in selected_words:
            self.to_define_word.emit(word.data(Qt.UserRole), Status.TO_BE_DEFINED)
            self.list_widget.takeItem(self.list_widget.row(word))
        self.save_words_to_model.emit()
        self.start_defining_words.emit(1)

    def delete_words(self):
        selected_words = self.list_widget.selectedItems()

        ids = []
        for word in selected_words:
            ids.append(word.data(Qt.UserRole))
            self.list_widget.takeItem(self.list_widget.row(word))
        self.delete_words_model.emit(ids)
        self.save_words_to_model.emit()

    @Slot(str, bool)
    def receive_settings_update(self, apple_note, apple_note_verified):
        self.apple_note_name = apple_note
        self.apple_note_verified = apple_note_verified
