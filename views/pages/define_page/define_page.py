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
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from components.dialogs.multi_selection import MultiSelectionDialog
from components.helpers import WidgetFactory
from core import WordLookupWorker
from models import WordModel, WordsModel


class DefinePage(QWidget):
    save_words_to_model = Signal()
    user_definition_selection = Signal(list)
    user_word_selection = Signal(int)
    add_word_to_define_queue = Signal(WordModel)

    def __init__(self):
        super().__init__()
        self.to_be_defined_queue = []
        word_set_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()

        self.arrow_up = QPushButton("")
        self.arrow_down = QPushButton("")
        self.arrow_down.setCursor(Qt.PointingHandCursor)
        self.arrow_up.setCursor(Qt.PointingHandCursor)

        self.word_lookup_thread = None

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
        self.defined_list_widget = QListWidget()
        self.skipped_list_widget = QListWidget()

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

        word_set_layout.addWidget(self.defined_list_widget)
        word_set_layout.addWidget(self.skipped_list_widget)

        self.wordsModel = WordsModel()
        # SLOTS / SIGNALS
        self.arrow_up.clicked.connect(self.navigate_up)
        self.arrow_down.clicked.connect(self.navigate_down)

        self.wordsModel.word_added_to_be_defined.connect(self.add_word)

        for word in self.wordsModel.to_be_defined_words:
            self.add_word(word)
        print("111********************")
        print(self.wordsModel.to_be_defined_words)
        print("********************")

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
        self.to_be_defined_queue.append(word)
        print("222********************")
        print(self.wordsModel.to_be_defined_words)
        print("********************")

        if self.word_lookup_thread and self.word_lookup_thread.isRunning():
            self.add_word_to_define_queue.emit(self.word_lookup_thread.add_word_to_list)

    @Slot(int)
    def start_define_words(self):
        print("here")
        print("333********************")
        print(self.wordsModel.to_be_defined_words)
        print("********************")
        if self.word_lookup_thread and self.word_lookup_thread.isRunning():
            pass
        else:
            self.word_lookup = WordLookupWorker(self.wordsModel.to_be_defined_words)
            self.word_lookup.multi_definitions.connect(self.select_definitions)
            self.word_lookup.multi_words.connect(self.select_word)
            self.user_definition_selection.connect(
                self.word_lookup.get_user_definition_selection
            )
            self.user_word_selection.connect(self.word_lookup.get_user_word_selection)
            self.word_lookup.defined_word.connect(self.receive_defined_word)
            self.word_lookup.skipped_word.connect(self.receive_skipped_word)
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

    def select_definitions(self, word, definitions):
        print("********", definitions)
        choices = [
            f"{definition.partOfSpeech} - {definition.definition}"
            for definition in definitions
        ]
        self.multi_dialog = MultiSelectionDialog(
            choices, f"{word} - Found Multiple Definitions", "Choose a Defintion", False
        )
        self.multi_dialog.md_multi_def_signal.connect(self.receive_definition_selection)
        self.multi_dialog.exec()

    def receive_word_selection(self, choice):
        self.user_word_selection.emit(choice[0])

    def receive_definition_selection(self, choices):
        print(choices)
        self.user_definition_selection.emit(choices)

    def receive_defined_word(self, word):
        print("defined words", word)
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.defined_list_widget.addItem(list_item)

        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def receive_skipped_word(self, word):
        print("skipped words", word)

        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.skipped_list_widget.addItem(list_item)

        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))
