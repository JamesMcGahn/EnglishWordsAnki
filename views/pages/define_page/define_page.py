from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from components.dialogs import EditWordDialog, MultiSelectionDialog
from core import WordLookupWorker
from models import Status, WordModel, WordsModel


class DefinePage(QWidget):
    start_audio_for_words = Signal(int)
    save_words_to_model = Signal()
    user_definition_selection = Signal(list)
    user_word_selection = Signal(int)
    add_word_to_define_queue = Signal(WordModel)
    update_word_model = Signal(str, WordModel)
    change_status = Signal(str, Status)

    def __init__(self):
        super().__init__()
        self.to_be_defined_queue = []
        word_set_layout = QVBoxLayout(self)

        self.word_lookup_thread = None

        # List Widget
        define_queue_qv = QVBoxLayout()
        word_set_layout.addLayout(define_queue_qv)
        self.list_widget = QListWidget()
        queue_buttons_layout = QHBoxLayout()
        define_queue_qv.addWidget(self.list_widget)
        define_queue_qv.addLayout(queue_buttons_layout)

        self.start_define = QPushButton("Start Defining")
        queue_buttons_layout.addWidget(self.start_define)

        self.bottom_list_widgets = QHBoxLayout()

        self.skipped_box = QVBoxLayout()
        self.definded_box = QVBoxLayout()

        self.bottom_list_widgets.addLayout(self.skipped_box)
        self.bottom_list_widgets.addLayout(self.definded_box)

        # SKIPPED BOX
        self.skipped_list_widget = QListWidget()
        self.skipped_box.addWidget(self.skipped_list_widget)
        self.edit_word_btn = QPushButton("Edit Word")
        self.move_word_to_queue_btn = QPushButton("Move Word to Queue")
        self.h_skipped_layout = QHBoxLayout()
        self.h_skipped_layout.addWidget(self.edit_word_btn)
        self.h_skipped_layout.addWidget(self.move_word_to_queue_btn)
        self.skipped_box.addLayout(self.h_skipped_layout)

        # DEFINED BOX
        self.defined_list_widget = QListWidget()
        self.defined_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.definded_box.addWidget(self.defined_list_widget)
        self.h_defined_layout = QHBoxLayout()

        self.get_audio_btn = QPushButton("Get Audio for Words")
        self.h_defined_layout.addWidget(self.get_audio_btn)

        self.definded_box.addLayout(self.h_defined_layout)

        word_set_layout.addLayout(self.bottom_list_widgets)

        self.wordsModel = WordsModel()
        # SLOTS / SIGNALS
        self.start_define.clicked.connect(self.start_define_words)
        self.wordsModel.word_added_to_be_defined.connect(self.add_word)
        self.edit_word_btn.clicked.connect(self.edit_skipped_word)
        self.move_word_to_queue_btn.clicked.connect(self.move_word_to_queue)
        self.save_words_to_model.connect(self.wordsModel.save_words)
        self.update_word_model.connect(self.wordsModel.update_word)
        self.get_audio_btn.clicked.connect(self.start_audio_words)
        self.change_status.connect(self.wordsModel.update_status)
        for word in self.wordsModel.to_be_defined_words:
            self.add_word(word)

    def edit_skipped_word(self):
        item = self.skipped_list_widget.currentItem()
        if item:
            guid = item.data(Qt.UserRole)
            word = [
                word
                for word in self.wordsModel.skipped_defined_words
                if word.guid == guid
            ]
            if word:
                edit_word = word[0]
                self.edit_word_dialog = EditWordDialog(
                    edit_word, "Edit Word", "Edit Word"
                )
                self.edit_word_dialog.updated_word.connect(self.update_edited_word)
                self.edit_word_dialog.exec()

    def update_edited_word(self, word):
        print(word)
        word.status = Status.TO_BE_DEFINED
        self.add_word(word)
        self.update_word_model.emit(word.guid, word)
        for index in range(self.skipped_list_widget.count()):
            item = self.skipped_list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.skipped_list_widget.takeItem(self.skipped_list_widget.row(item))

    def move_word_to_queue(self):
        item = self.skipped_list_widget.currentItem()
        if item:
            guid = item.data(Qt.UserRole)
            word = [
                word
                for word in self.wordsModel.skipped_defined_words
                if word.guid == guid
            ]
            if word:
                change_word = word[0]
                self.change_status.emit(change_word.guid, Status.TO_BE_DEFINED)
                for index in range(self.skipped_list_widget.count()):
                    item = self.skipped_list_widget.item(index)
                    if item and item.data(Qt.UserRole) == change_word.guid:
                        self.skipped_list_widget.takeItem(
                            self.skipped_list_widget.row(item)
                        )

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

        if self.word_lookup_thread and self.word_lookup_thread.isRunning():
            self.add_word_to_define_queue.emit(self.word_lookup_thread.add_word_to_list)

    @Slot(int)
    def start_define_words(self):
        if self.word_lookup_thread and self.word_lookup_thread.isRunning():
            return
        else:
            self.start_define.setDisabled(True)
            self.word_lookup = WordLookupWorker(self.wordsModel.to_be_defined_words)
            self.word_lookup.multi_definitions.connect(self.select_definitions)
            self.word_lookup.multi_words.connect(self.select_word)
            self.user_definition_selection.connect(
                self.word_lookup.get_user_definition_selection
            )
            self.user_word_selection.connect(self.word_lookup.get_user_word_selection)
            self.word_lookup.defined_word.connect(self.receive_defined_word)
            self.word_lookup.skipped_word.connect(self.receive_skipped_word)
            self.word_lookup.finished.connect(
                lambda: self.start_define.setDisabled(False)
            )
            self.word_lookup.finished.connect(lambda: self.save_words_to_model.emit())
            self.word_lookup.start()

    def select_word(self, words):
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
        self.user_definition_selection.emit(choices)

    def receive_defined_word(self, word):
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.defined_list_widget.addItem(list_item)
        self.update_word_model.emit(word.guid, word)
        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def receive_skipped_word(self, word):
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.skipped_list_widget.addItem(list_item)

        for index in range(self.list_widget.count()):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def start_audio_words(self):
        self.defined_list_widget.selectAll()
        selected_words = self.defined_list_widget.selectedItems()
        for word in selected_words:
            self.change_status.emit(word.data(Qt.UserRole), Status.TO_BE_AUDIO)
            self.defined_list_widget.takeItem(self.defined_list_widget.row(word))
        self.save_words_to_model.emit()
        self.start_audio_for_words.emit(2)
