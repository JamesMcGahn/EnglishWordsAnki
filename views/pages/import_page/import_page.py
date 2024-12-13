import uuid

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.helpers import WidgetFactory
from core.apple_note_import import AppleNoteImport
from models import Status, WordModel, WordsModel


class ImportPage(QWidget):
    add_word_to_model = Signal(WordModel)
    save_words_to_model = Signal()
    to_define_word = Signal(str)

    def __init__(self):
        super().__init__()
        self.word_list = []
        word_set_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()

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

        # Rule Set Details
        details_layout = QFormLayout()
        details_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.word_set_name = QLineEdit()
        self.word_set_description = QTextEdit()
        self.word_set_name_label = QLabel("Word:")
        self.word_set_name_label.setAlignment(Qt.AlignLeft)

        details_layout.addRow(self.word_set_name_label, self.word_set_name)

        word_set_layout.addLayout(details_layout)
        self.import_btn = QPushButton("Import")
        self.start_define_btn = QPushButton("Define Selected Words")
        word_set_layout.addWidget(self.import_btn)
        word_set_layout.addWidget(self.start_define_btn)

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
        self.to_define_word.connect(self.wordsModel.add_word_to_be_defined)

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
        self.appleNoteThread = QThread()
        self.appleNoteThread.start()
        self.appleImport = AppleNoteImport("Words")
        self.appleImport.moveToThread(self.appleNoteThread)
        self.appleImport.result.connect(self.receive_words)
        self.appleImport.finished.connect(self.appleImport.deleteLater)
        self.appleImport.finished.connect(self.appleNoteThread.quit)

        self.appleImport.start_work.emit()

    def receive_words(self, words):
        for word in words:
            new_word = WordModel(Status.ADDED, str(uuid.uuid4()), word, "", "", "", "")
            self.add_word_to_model.emit(new_word)
        self.save_words_to_model.emit()

    def start_define_words(self):
        selected_words = self.list_widget.selectedItems()

        for word in selected_words:
            print(word.text())
            print(word.data(Qt.UserRole))
            self.to_define_word.emit(word.data(Qt.UserRole))
            self.list_widget.takeItem(self.list_widget.row(word))
        self.save_words_to_model.emit()
