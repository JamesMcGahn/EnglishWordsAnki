import os

from PySide6.QtCore import QRect, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)

from base import QWidgetBase
from core import AppleNoteImport
from models import LogSettingsModel
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials


class SettingsPage(QWidgetBase):
    folder_submit = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.settings_page_layout = QVBoxLayout(self)
        self.running_tasks = {}

        self.x_icon = QIcon()
        self.x_icon.addFile(
            ":/images/red_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self.check_icon = QIcon()
        self.check_icon.addFile(
            ":/images/green_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self.folder_icon = QIcon()
        self.folder_icon.addFile(
            ":/images/open_folder_on.png",
            QSize(),
            QIcon.Mode.Normal,
        )

        hspacer = QSpacerItem(400, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.settings_page_layout.addItem(hspacer)

        (
            self.lineEdit_apple_note,
            self.label_apple_note_verfied,
            self.label_apple_note_verify_btn,
            self.apple_note_hlayout,
        ) = self.create_input_fields("Apple Note Name:", "Verify Apple Note")
        (
            self.lineEdit_anki_words_deck,
            self.label_anki_words_deck_verfied,
            self.label_anki_words_verify_btn,
            self.anki_words_deck_hlayout,
        ) = self.create_input_fields("Word's Deck Name:", "Verify Deck")

        (
            self.lineEdit_anki_model_deck,
            self.label_anki_model_deck_verfied,
            self.label_anki_model_verify_btn,
            self.anki_model_deck_hlayout,
        ) = self.create_input_fields("Word's Model Name:", "Verify Model")

        (
            self.lineEdit_anki_user,
            self.label_anki_user_verfied,
            self.label_anki_user_verify_btn,
            self.anki_user_hlayout,
        ) = self.create_input_fields("Anki User Name:", "Verify User")
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_path_hlayout,
            self.anki_audio_path_folder_btn,
        ) = self.create_input_fields(
            "Anki Audio path:", "Verify Audio Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_path,
            self.label_log_file_path_verfied,
            self.label_log_file_path_verify_btn,
            self.log_file_path_hlayout,
            self.log_file_path_folder_btn,
        ) = self.create_input_fields(
            "Log File path:", "Verify Log Path", folder_icon=True
        )
        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verfied,
            self.label_google_api_key_verify_btn,
            self.google_api_key_hlayout,
        ) = self.create_input_fields("Google Service:", "Verify Google Service", False)

        self.settings_page_layout.addLayout(self.apple_note_hlayout)
        self.settings_page_layout.addLayout(self.anki_words_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_model_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_user_hlayout)
        self.settings_page_layout.addLayout(self.anki_audio_path_hlayout)
        self.settings_page_layout.addLayout(self.log_file_path_hlayout)
        self.settings_page_layout.addLayout(self.google_api_key_hlayout)
        self.settings_page_layout.addItem(vspacer)

        self.secure_creds = SecureCredentials()
        self.settings = AppSettings()
        self.log_settings = LogSettingsModel()
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        self.get_settings("ALL", setText=True)
        self.folder_submit.connect(self.folder_change)
        self.label_apple_note_verify_btn.clicked.connect(self.verify_apple_note_name)
        self.label_anki_words_verify_btn.clicked.connect(self.verify_deck_name)
        self.label_anki_model_verify_btn.clicked.connect(self.verify_deck_model)
        self.label_anki_user_verify_btn.clicked.connect(self.verify_anki_user)
        self.label_anki_audio_path_verify_btn.clicked.connect(
            lambda: self.open_folder_dialog("audio_path", self.lineEdit_anki_audio_path)
        )
        self.label_log_file_path_verify_btn.clicked.connect(
            lambda: self.open_folder_dialog(
                "log_file_path", self.lineEdit_log_file_path
            )
        )

        self.log_file_path_folder_btn.clicked.connect(
            lambda: self.open_folder_dialog(
                "log_file_path", self.lineEdit_log_file_path
            )
        )
        self.anki_audio_path_folder_btn.clicked.connect(
            lambda: self.open_folder_dialog("audio_path", self.lineEdit_log_file_path)
        )
        self.lineEdit_apple_note.textChanged.connect(
            lambda word, field="apple_note": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_anki_words_deck.textChanged.connect(
            lambda word, field="words": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_anki_model_deck.textChanged.connect(
            lambda word, field="model": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_anki_user.textChanged.connect(
            lambda word, field="user": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_anki_audio_path.textChanged.connect(
            lambda word, field="audio_path": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_log_file_path.textChanged.connect(
            lambda word, field="log_file_path": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.textEdit_google_api_key.textChanged.connect(
            lambda field="google_api": self.textEdit_change_secure_setting(
                field, self.textEdit_google_api_key
            )
        )

    def textEdit_change_secure_setting(self, field, text_edit):
        text = text_edit.toPlainText()
        self.change_secure_setting(field, text, setting_type=field)

    def get_settings(self, setting="ALL", setText=False):
        self.settings.begin_group("settings")

        def words_deck():
            self.words_deck, self.words_verified = self.get_and_set_settings(
                "words",
                "",
                self.lineEdit_anki_words_deck,
                self.label_anki_words_deck_verfied,
                self.label_anki_words_verify_btn,
                setText,
            )

        def model_deck():
            self.model_deck, self.model_verified = self.get_and_set_settings(
                "model",
                "",
                self.lineEdit_anki_model_deck,
                self.label_anki_model_deck_verfied,
                self.label_anki_model_verify_btn,
                setText,
            )

        def anki_user():
            self.anki_user, self.anki_user_verified = self.get_and_set_settings(
                "user",
                "User 1",
                self.lineEdit_anki_user,
                self.label_anki_user_verfied,
                self.label_anki_user_verify_btn,
                setText,
            )

        def anki_audio_path():
            self.anki_audio, self.anki_audio_verified = self.get_and_set_settings(
                "audio_path",
                f"{self.home_directory}/Library/Application Support/Anki2/{self.anki_user}/collection.media",
                self.lineEdit_anki_audio_path,
                self.label_anki_audio_path_verfied,
                self.label_anki_audio_path_verify_btn,
                setText,
            )

        def apple_note():
            self.apple_note, self.apple_note_verified = self.get_and_set_settings(
                "apple_note",
                f"{self.home_directory}/Library/Application Support/Anki2/{self.anki_user}/collection.media",
                self.lineEdit_apple_note,
                self.label_apple_note_verfied,
                self.label_apple_note_verify_btn,
                setText,
            )

        def google_api():
            value = self.secure_creds.get_creds(
                "english-dict-secure-settings", "google_api"
            )
            verified = self.settings.get_value("google_api-verified", False)

            self.textEdit_google_api_key.setText(value)
            self.label_google_api_key_verfied.setIcon(
                self.check_icon if verified else self.x_icon
            )
            self.label_google_api_key_verify_btn.setDisabled(verified)

        def log_file_path():
            self.log_file_path, self.log_file_path_verified = self.get_and_set_settings(
                "log_file_path",
                "./logs/",
                self.lineEdit_log_file_path,
                self.label_log_file_path_verfied,
                self.label_log_file_path_verify_btn,
                setText,
            )
            # TODO connect to the logsettings saved signal to update logging

        match setting:
            case "words":
                words_deck()
            case "model":
                model_deck()
            case "user":
                anki_user()
            case "audio_path":
                anki_audio_path()
            case "apple_note":
                apple_note()
            case "google_api":
                google_api()
            case "log_file_path":
                log_file_path()

            case "ALL":
                words_deck()
                model_deck()
                anki_user()
                anki_audio_path()
                apple_note()
                google_api()
                log_file_path()
        self.settings.end_group()

    def get_and_set_settings(
        self, key, default, lineEdit, verify_icon_btn, verify_btn, setText=False
    ):
        value = self.settings.get_value(key, default)
        verified = self.settings.get_value(f"{key}-verified", False)
        print(key, value, verified)
        if setText:
            lineEdit.setText(value)
        verify_icon_btn.setIcon(self.check_icon if verified else self.x_icon)
        verify_btn.setDisabled(verified)
        return value, verified

    def run_network_check(
        self, task_id, url, json_data, success_callback, error_callback, btn
    ):
        network_thread = QThread(self)

        worker = NetworkWorker(url, json=json_data, timeout=25)
        worker.moveToThread(network_thread)

        # Signal-Slot Connections
        worker.response.connect(success_callback)
        worker.error.connect(error_callback)
        network_thread.started.connect(worker.do_work)
        worker.finished.connect(lambda: self.cleanup_task(task_id))
        network_thread.finished.connect(network_thread.deleteLater)
        self.running_tasks[task_id] = (network_thread, worker)
        # Disable Button & Start Thread
        btn.setDisabled(True)
        network_thread.start()

    def cleanup_task(self, task_id):
        if task_id in self.running_tasks:
            _, worker = self.running_tasks.pop(task_id)
            worker.deleteLater()
            print(f"Task {task_id} cleaned up.")

    def verify_apple_note_name(self):
        self.label_apple_note_verify_btn.setDisabled(False)
        self.apple_note_thread = QThread(self)
        self.apple_worker = AppleNoteImport(self.lineEdit_apple_note.text())
        self.apple_worker.moveToThread(self.apple_note_thread)
        self.apple_worker.note_name_verified.connect(self.apple_note_response)
        self.apple_note_thread.finished.connect(self.deleteLater)
        self.apple_note_thread.started.connect(self.apple_worker.verify_note_name)
        self.apple_worker.finished.connect(self.apple_worker.deleteLater)
        self.apple_note_thread.start()

    def verify_deck_name(self):
        json_data = {"action": "deckNames", "version": 6}
        print("here")
        self.run_network_check(
            "verify_deck_name",
            "http://127.0.0.1:8765/",
            json_data,
            self.deck_response,
            lambda: self.label_anki_words_verify_btn.setDisabled(False),
            self.label_anki_words_verify_btn,
        )

    def verify_deck_model(self):
        json_data = {"action": "modelNames", "version": 6}
        self.run_network_check(
            "verify_deck_model",
            "http://127.0.0.1:8765/",
            json_data,
            self.model_response,
            lambda: self.label_anki_model_verify_btn.setDisabled(False),
            self.label_anki_model_verify_btn,
        )

    def verify_anki_user(self):
        json_data = {"action": "getProfiles", "version": 6}
        self.run_network_check(
            "verify_anki_user",
            "http://127.0.0.1:8765/",
            json_data,
            self.user_response,
            lambda: self.label_anki_user_verify_btn.setDisabled(False),
            self.label_anki_user_verify_btn,
        )

    def change_setting(self, field, value, verified=False, setting_type="ALL"):
        print(field, value)
        self.settings.begin_group("settings")
        self.settings.set_value(field, value)
        self.settings.set_value(f"{field}-verified", verified)
        self.settings.end_group()
        self.get_settings(setting_type, setText=False)

    def change_secure_setting(self, field, value, verified=False, setting_type="ALL"):
        print(field, value)
        self.secure_creds.save_creds("english-dict-secure-settings", field, value)
        self.settings.begin_group("settings")
        self.settings.set_value(f"{field}-verified", verified)
        self.settings.end_group()
        self.get_settings(setting_type, setText=False)

    def response_update(
        self,
        response,
        key,
        value,
        icon_label,
        verify_btn,
        model_verified,
        setting_type="ALL",
    ):
        if value in response:
            self.change_setting(key, value, True, setting_type)
            icon_label.setIcon(self.check_icon)
            verify_btn.setDisabled(True)
            model_verified = True
        else:
            verify_btn.setDisabled(False)
            icon_label.setIcon(self.check_icon if model_verified else self.x_icon)

    @Slot(str, str)
    def folder_change(self, key, folder):
        if key == "log_file_path":
            self.verify_log_file_path(folder)
        elif key == "audio_path":
            self.verify_anki_user_audio_path(folder)

    def verify_anki_user_audio_path(self, folder):
        isExist = os.path.exists(folder)
        self.response_update(
            [f"{folder if isExist else False}"],
            "audio_path",
            folder,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_verified,
            "audio_path",
        )

    def verify_log_file_path(self, folder):

        isExist = os.path.exists(folder)
        self.response_update(
            [f"{folder if isExist else False}"],
            "log_file_path",
            folder,
            self.label_log_file_path_verfied,
            self.label_log_file_path_verify_btn,
            self.log_file_path_verified,
            "log_file_path",
        )

    def apple_note_response(self, response):
        self.response_update(
            [f"{self.apple_note if response else False}"],
            "apple_note",
            self.apple_note,
            self.label_apple_note_verfied,
            self.label_apple_note_verify_btn,
            self.apple_note_verified,
            "apple_note",
        )

    def deck_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "words",
            self.words_deck,
            self.label_anki_words_deck_verfied,
            self.label_anki_words_verify_btn,
            self.words_verified,
            "words",
        )

    def model_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "model",
            self.model_deck,
            self.label_anki_model_deck_verfied,
            self.label_anki_model_verify_btn,
            self.model_verified,
            "model",
        )

    def user_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "user",
            self.anki_user,
            self.label_anki_user_verfied,
            self.label_anki_user_verify_btn,
            self.anki_user_verified,
            "user",
        )

    def create_input_fields(
        self, label_text, verify_button_text, lineEdit=True, folder_icon=False
    ):
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)
        label = QLabel(label_text)
        label.setMinimumWidth(143)

        verify_icon_button = QPushButton()
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_button = QPushButton(verify_button_text)
        verify_button.setCursor(Qt.PointingHandCursor)

        h_layout.setSpacing(10)
        h_layout.addWidget(label)

        if lineEdit:
            line_edit_field = QLineEdit()
            line_edit_field.setMaximumWidth(230)
            h_layout.addWidget(line_edit_field)
        else:
            text_edit_field = QTextEdit()
            text_edit_field.setMaximumWidth(230)
            h_layout.addWidget(text_edit_field)
        h_layout.addWidget(verify_icon_button)
        h_layout.addWidget(verify_button)

        if folder_icon:
            folder_icon_button = QPushButton()
            folder_icon_button.setCursor(Qt.PointingHandCursor)
            folder_icon_button.setMaximumWidth(40)
            folder_icon_button.setStyleSheet("background:transparent;border: none;")
            folder_icon_button.setIcon(self.folder_icon)
            h_layout.addWidget(folder_icon_button)
            return (
                line_edit_field if lineEdit else text_edit_field,
                verify_icon_button,
                verify_button,
                h_layout,
                folder_icon_button,
            )
        return (
            line_edit_field if lineEdit else text_edit_field,
            verify_icon_button,
            verify_button,
            h_layout,
        )

    def open_folder_dialog(self, key, input_field) -> None:
        """
        Opens a dialog for the user to select a folder for storing log files.
        Once a folder is selected, the path is updated in the corresponding input field.

        Returns:
            None: This function does not return a value.
        """

        path = input_field.text() or "./"

        folder = QFileDialog.getExistingDirectory(self, "Select Folder", dir=path)

        if folder:
            input_field.blockSignals(True)
            input_field.setText(folder)
            input_field.blockSignals(False)
            self.folder_submit.emit(key, folder)
