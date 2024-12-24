from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from base import QWidgetBase
from components.dialogs import EditWordDialog
from core import AudioThread
from models import Status, WordModel, WordsModel


class AudioPage(QWidgetBase):
    save_words_to_model = Signal()
    add_word_to_audio_queue = Signal(WordModel)
    update_word_model = Signal(str, WordModel)
    change_status = Signal(str, Status)
    start_sync_for_words = Signal(int)

    def __init__(self):
        super().__init__()
        self.to_be_defined_queue = []
        word_set_layout = QVBoxLayout(self)

        self.audio_thread = None
        self.anki_audio_path = None
        self.google_api_key_string = None
        self.anki_audio_path_verified = None
        self.google_api_key_string_verified = None

        # List Widget
        define_queue_qv = QVBoxLayout()
        word_set_layout.addLayout(define_queue_qv)
        self.list_widget = QListWidget()
        queue_buttons_layout = QHBoxLayout()
        define_queue_qv.addWidget(self.list_widget)
        define_queue_qv.addLayout(queue_buttons_layout)

        self.start_define = QPushButton("Start Audio")
        queue_buttons_layout.addWidget(self.start_define)

        self.bottom_list_widgets = QHBoxLayout()

        self.skipped_box = QVBoxLayout()
        self.audio_downloaded_box = QVBoxLayout()

        self.bottom_list_widgets.addLayout(self.skipped_box)
        self.bottom_list_widgets.addLayout(self.audio_downloaded_box)

        # SKIPPED BOX
        self.errored_list_widget = QListWidget()
        self.skipped_box.addWidget(self.errored_list_widget)
        self.skip_audio_word_btn = QPushButton("Skip Audio")
        self.move_word_to_queue_btn = QPushButton("Move Word to Audio Queue")
        self.h_skipped_layout = QHBoxLayout()
        self.h_skipped_layout.addWidget(self.move_word_to_queue_btn)
        self.h_skipped_layout.addWidget(self.skip_audio_word_btn)

        self.skipped_box.addLayout(self.h_skipped_layout)

        # DEFINED BOX
        self.audio_downloaded_list_widget = QListWidget()
        self.audio_downloaded_box.addWidget(self.audio_downloaded_list_widget)
        self.h_defined_layout = QHBoxLayout()
        self.audio_downloaded_list_widget.setSelectionMode(QListWidget.MultiSelection)
        self.get_sync_btn = QPushButton("Sync Words to Anki")
        self.h_defined_layout.addWidget(self.get_sync_btn)

        self.audio_downloaded_box.addLayout(self.h_defined_layout)

        word_set_layout.addLayout(self.bottom_list_widgets)

        self.wordsModel = WordsModel()
        # SLOTS / SIGNALS
        self.start_define.clicked.connect(self.start_audio_words)
        self.wordsModel.word_added_to_be_audio.connect(self.add_word)
        self.skip_audio_word_btn.clicked.connect(self.move_error_word_to_sync)
        self.move_word_to_queue_btn.clicked.connect(self.move_word_to_queue)
        self.save_words_to_model.connect(self.wordsModel.save_words)
        self.update_word_model.connect(self.wordsModel.update_word)
        self.change_status.connect(self.wordsModel.update_status)
        self.get_sync_btn.clicked.connect(self.start_sync_words)

        for word in self.wordsModel.to_be_audio_words:
            self.add_word(word)

    def move_error_word_to_sync(self):
        word = self.remove_from_error_list()
        if word:
            list_item = QListWidgetItem(word.word)
            list_item.setData(Qt.UserRole, word.guid)
            self.audio_downloaded_list_widget.addItem(list_item)
            word.status = Status.AUDIO
            self.update_word_model.emit(word.guid, word)

    def move_word_to_queue(self):
        word = self.remove_from_error_list()
        if word:
            self.change_status.emit(word.guid, Status.TO_BE_AUDIO)

    def remove_from_error_list(self):
        item = self.errored_list_widget.currentItem()
        if item:
            guid = item.data(Qt.UserRole)
            word = [
                word
                for word in self.wordsModel.skipped_audio_words
                if word.guid == guid
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

        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.list_widget.addItem(list_item)

        if self.audio_thread and self.audio_thread.isRunning():
            self.add_word_to_audio_queue.emit(word)

    @Slot(int)
    def start_audio_words(self):
        if self.audio_thread and self.audio_thread.isRunning():
            return
        elif not self.wordsModel.to_be_audio_words:
            return
        elif not self.google_api_key_string:
            self.log_with_toast(
                "Google API Key String Not Set",
                "Please enter the Google API Key on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        elif not self.google_api_key_string_verified:
            self.log_with_toast(
                "Google API Key Not Verfied",
                "Please verify the Google API Key on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        elif not self.anki_audio_path:
            self.log_with_toast(
                "Anki Audio Path Not Set",
                "Please enter the Anki audio path on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        elif not self.anki_audio_path_verified:
            self.log_with_toast(
                "Anki Audio Path Not Verified",
                "Please verify the Anki audio path on the Settings page.",
                "WARN",
                "WARN",
                parent=self,
            )
            return
        else:
            self.start_define.setDisabled(True)
            self.audio_thread = AudioThread(
                self.wordsModel.to_be_audio_words,
                folder_path=self.anki_audio_path,
                credential_string=self.google_api_key_string,
            )

            self.audio_thread.audio_word.connect(self.receive_audio_word)
            self.audio_thread.error_word.connect(self.receive_error_word)

            self.audio_thread.finished.connect(
                lambda: self.start_define.setDisabled(False)
            )
            self.audio_thread.finished.connect(lambda: self.save_words_to_model.emit())
            self.audio_thread.finished.connect(self.reset_thread_reference)
            self.add_word_to_audio_queue.connect(self.audio_thread.add_word_to_list)
            self.audio_thread.start()

    def reset_thread_reference(self):
        if self.audio_thread and self.audio_thread.isRunning():
            self.audio_thread.quit()
            self.audio_thread.wait()
            self.audio_thread.deleteLater()
            self.audio_thread = None

    def receive_audio_word(self, word):
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.audio_downloaded_list_widget.addItem(list_item)
        self.update_word_model.emit(word.guid, word)
        for index in reversed(range(self.list_widget.count())):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def receive_error_word(self, word):
        list_item = QListWidgetItem(word.word)
        list_item.setData(Qt.UserRole, word.guid)
        self.errored_list_widget.addItem(list_item)

        for index in reversed(range(self.list_widget.count())):
            item = self.list_widget.item(index)
            if item and item.data(Qt.UserRole) == word.guid:
                self.list_widget.takeItem(self.list_widget.row(item))

    def start_sync_words(self):
        self.audio_downloaded_list_widget.selectAll()
        selected_words = self.audio_downloaded_list_widget.selectedItems()
        print(selected_words)
        for word in selected_words:
            self.change_status.emit(word.data(Qt.UserRole), Status.TO_BE_SYNCED)
            self.audio_downloaded_list_widget.takeItem(
                self.audio_downloaded_list_widget.row(word)
            )
        self.save_words_to_model.emit()
        self.start_sync_for_words.emit(3)

    @Slot(str, bool, str, bool)
    def receive_settings_update(
        self,
        google_api_key_string,
        google_api_key_string_verified,
        anki_audio_path,
        anki_audio_path_verified,
    ):
        print(
            "audio page",
            google_api_key_string,
            google_api_key_string_verified,
            anki_audio_path,
            anki_audio_path_verified,
        )
        self.google_api_key_string = google_api_key_string
        self.google_api_key_string_verified = google_api_key_string_verified
        self.anki_audio_path = anki_audio_path
        self.anki_audio_path_verified = anki_audio_path_verified
