from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import AnkiExportThread, RemoveDuplicateAudio
from models import Status, WordModel, WordsModel


class SyncPage(QWidget):
    save_words_to_model = Signal()
    add_word_to_sync_queue = Signal(WordModel)
    update_word_model = Signal(str, WordModel)
    change_status = Signal(str, Status)
    start_sync_for_words = Signal(int)
    delete_words = Signal(list)

    def __init__(self):
        super().__init__()
        self.to_be_defined_queue = []
        word_set_layout = QVBoxLayout(self)

        self.anki_thread = None

        # List Widget
        define_queue_qv = QVBoxLayout()
        word_set_layout.addLayout(define_queue_qv)
        self.list_widget = QListWidget()
        queue_buttons_layout = QHBoxLayout()
        define_queue_qv.addWidget(self.list_widget)
        define_queue_qv.addLayout(queue_buttons_layout)

        self.start_sync_btn = QPushButton("Start Sync")
        queue_buttons_layout.addWidget(self.start_sync_btn)

        self.bottom_list_widgets = QHBoxLayout()

        self.skipped_box = QVBoxLayout()
        self.definded_box = QVBoxLayout()

        self.bottom_list_widgets.addLayout(self.skipped_box)
        self.bottom_list_widgets.addLayout(self.definded_box)

        # SKIPPED BOX
        self.errored_list_widget = QListWidget()
        self.skipped_box.addWidget(self.errored_list_widget)
        self.remove_duplicates_btn = QPushButton("Remove Duplicates")
        self.move_word_to_queue_btn = QPushButton("Try Sync Again")
        self.h_skipped_layout = QHBoxLayout()
        self.h_skipped_layout.addWidget(self.move_word_to_queue_btn)
        self.h_skipped_layout.addWidget(self.remove_duplicates_btn)

        self.skipped_box.addLayout(self.h_skipped_layout)

        # DEFINED BOX
        self.defined_list_widget = QListWidget()
        self.definded_box.addWidget(self.defined_list_widget)
        self.h_defined_layout = QHBoxLayout()

        self.definded_box.addLayout(self.h_defined_layout)

        word_set_layout.addLayout(self.bottom_list_widgets)

        self.wordsModel = WordsModel()
        # SLOTS / SIGNALS
        self.start_sync_btn.clicked.connect(self.start_sync_words)
        self.wordsModel.word_added_to_be_sync.connect(self.add_word)
        self.remove_duplicates_btn.clicked.connect(self.remove_duplicates)
        self.move_word_to_queue_btn.clicked.connect(self.move_word_to_queue)
        self.save_words_to_model.connect(self.wordsModel.save_words)
        self.update_word_model.connect(self.wordsModel.update_word)
        self.change_status.connect(self.wordsModel.update_status)
        self.delete_words.connect(self.wordsModel.delete_words)

        for word in self.wordsModel.to_be_synced_words:
            self.add_word(word)

    def remove_duplicates(self):
        guids = []
        paths = []
        for word in self.wordsModel.skipped_sync_duplicates:
            print(word.word)
            guids.append(word.guid)
            paths.append(word.audio_path)

        self.remove_duplicates_btn.setDisabled(True)
        self.removal_thread = QThread(self)
        self.removal_worker = RemoveDuplicateAudio(paths)
        self.removal_worker.moveToThread(self.removal_thread)
        self.removal_thread.started.connect(self.removal_worker.do_work)
        self.removal_worker.finished.connect(
            lambda: self.on_file_removal_completed(guids)
        )
        self.removal_thread.finished.connect(self.removal_worker.deleteLater)
        self.removal_thread.finished.connect(self.removal_thread.deleteLater)
        self.removal_thread.start()

    def on_file_removal_completed(self, guids):

        self.delete_words.emit(guids)
        for index in reversed(range(self.errored_list_widget.count())):
            item = self.errored_list_widget.item(index)
            if item and item.data(Qt.UserRole) in guids:
                self.errored_list_widget.takeItem(self.errored_list_widget.row(item))
        self.remove_duplicates_btn.setDisabled(False)

    def move_word_to_queue(self):
        word = self.remove_from_error_list()
        if word:
            self.change_status.emit(word.guid, Status.TO_BE_SYNCED)

    def remove_from_error_list(self):
        item = self.errored_list_widget.currentItem()
        if item:
            guid = item.data(Qt.UserRole)
            word = [
                word for word in self.wordsModel.skipped_sync_error if word.guid == guid
            ]
            if word:
                change_word = word[0]

                for index in reversed(range(self.errored_list_widget.count())):
                    item = self.errored_list_widget.item(index)
                    if item and item.data(Qt.UserRole) == change_word.guid:
                        self.errored_list_widget.takeItem(
                            self.errored_list_widget.row(item)
                        )
                return change_word
        return False

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
        print("received to be sync ********", word)
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.list_widget.addItem(list_item)

        if self.anki_thread and self.anki_thread.isRunning():
            self.add_word_to_sync_queue.emit(word)

    @Slot(int)
    def start_sync_words(self):
        if self.anki_thread and self.anki_thread.isRunning():
            return
        else:
            print("hereeee")
            print(self.wordsModel.to_be_synced_words)
            self.start_sync_btn.setDisabled(True)
            self.anki_thread = AnkiExportThread(
                self.wordsModel.to_be_synced_words, "English Words", "English Vocab"
            )
            self.anki_thread.error_word.connect(
                lambda word: self.receive_error_word(word, False)
            )
            self.anki_thread.dup_word.connect(
                lambda word: self.receive_error_word(word, True)
            )
            self.anki_thread.finished.connect(self.on_anki_thread_completed)
            self.anki_thread.synced_word.connect(self.receive_synced_word)
            self.add_word_to_sync_queue.connect(self.anki_thread.add_word_to_list)
            self.anki_thread.start()

    def on_anki_thread_completed(self):
        self.save_words_to_model.emit()
        self.reset_thread_reference()
        self.start_sync_btn.setDisabled(False)

    def reset_thread_reference(self):
        if self.anki_thread and self.anki_thread.isRunning():
            self.anki_thread.quit()
            self.anki_thread.wait()
            self.anki_thread.deleteLater()
            self.anki_thread = None

    def receive_synced_word(self, word):
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.defined_list_widget.addItem(list_item)
        self.update_word_model.emit(word.guid, word)
        self.change_status.emit(word.guid, Status.ANKI_SYNCED)
        for index in reversed(range(self.list_widget.count())):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def receive_error_word(self, word, dup):
        list_item = QListWidgetItem(f"{word.word}{' - Duplicate' if dup else ''}")
        list_item.setData(Qt.UserRole, word.guid)
        self.errored_list_widget.addItem(list_item)

        for index in reversed(range(self.list_widget.count())):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))
