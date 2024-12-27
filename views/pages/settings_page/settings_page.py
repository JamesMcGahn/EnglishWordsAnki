import os

from PySide6.QtCore import QRect, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
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
from core import AppleNoteImport, AudioThread, RemoveDuplicateAudio
from models import LogSettingsModel, Status, WordModel
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials


class SettingsPage(QWidgetBase):
    folder_submit = Signal(str, str)
    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()
        self.settings_page_layout = QHBoxLayout(self)
        self.inner_settings_page_layout = QHBoxLayout()
        self.settings_page_layout.addLayout(self.inner_settings_page_layout)
        self.vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_page_layout.addItem(self.vspacer)
        self.running_tasks = {}
        self.settings = AppSettings()
        self.log_settings = LogSettingsModel()

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

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hspacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.settings_page_layout.addItem(self.hspacer)

        # self.settings_page_layout.addItem(hspacer)
        self.settings_grid_layout = QGridLayout()
        self.columns = 4
        self.settings_page_layout.addLayout(self.settings_grid_layout)
        self.settings_page_layout.addItem(self.hspacer1)
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
            self.lineEdit_log_file_name,
            self.label_log_file_name_verfied,
            self.label_log_file_name_verify_btn,
            self.log_file_name_hlayout,
        ) = self.create_input_fields("Log File Name:", "Save Log File Name")
        (
            self.lineEdit_log_backup_count,
            self.label_log_backup_count_verfied,
            self.label_log_backup_count_verify_btn,
            self.log_backup_count_hlayout,
        ) = self.create_input_fields("Log Backup Count:", "Save Log Backup Count")
        (
            self.lineEdit_log_file_max_mbs,
            self.label_log_file_max_mbs_verfied,
            self.label_log_file_max_mbs_verify_btn,
            self.log_file_max_mbs_hlayout,
        ) = self.create_input_fields("Log File Max Mbs:", "Save Log File Max Mbs")
        (
            self.lineEdit_log_keep_files_days,
            self.label_log_keep_files_days_verfied,
            self.label_log_keep_files_days_verify_btn,
            self.log_keep_files_days_hlayout,
        ) = self.create_input_fields("Keep Log File Days:", "Save Log File Days")
        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verfied,
            self.label_google_api_key_verify_btn,
            self.google_api_key_vlayout,
        ) = self.create_input_fields("Google Service:", "Verify Google Service", False)
        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )
        self.google_auth_api_key_paste_btn = QPushButton("Paste API Key")
        self.google_api_key_vlayout.addWidget(self.google_auth_api_key_paste_btn)
        self.settings_page_layout.addItem(self.vspacer3)

        self.secure_creds = SecureCredentials()

        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        self.get_settings("ALL", setText=True)

        self.folder_submit.connect(self.folder_change)
        self.save_log_settings_model.connect(self.log_settings.save_log_settings)
        self.label_apple_note_verify_btn.clicked.connect(self.verify_apple_note_name)
        self.label_anki_words_verify_btn.clicked.connect(self.verify_deck_name)
        self.label_anki_model_verify_btn.clicked.connect(self.verify_deck_model)
        self.label_anki_user_verify_btn.clicked.connect(self.verify_anki_user)
        self.label_google_api_key_verify_btn.clicked.connect(self.verify_google_api_key)
        self.label_log_file_name_verify_btn.clicked.connect(self.verify_log_file_name)
        self.label_log_backup_count_verify_btn.clicked.connect(
            self.verify_log_backup_count
        )
        self.label_log_file_max_mbs_verify_btn.clicked.connect(
            self.verify_log_file_max_mbs
        )
        self.label_log_keep_files_days_verify_btn.clicked.connect(
            self.verify_log_keep_files_days
        )
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
            lambda: self.open_folder_dialog("audio_path", self.lineEdit_anki_audio_path)
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
        self.lineEdit_log_file_name.textChanged.connect(
            lambda word, field="log_file_name": self.change_setting(
                field, word, setting_type=field
            )
        )
        self.lineEdit_log_backup_count.textChanged.connect(
            lambda word, field="log_backup_count": self.change_setting(
                field, word, setting_type=field, type="int"
            )
        )
        self.lineEdit_log_file_max_mbs.textChanged.connect(
            lambda word, field="log_file_max_mbs": self.change_setting(
                field, word, setting_type=field, type="int"
            )
        )
        self.lineEdit_log_keep_files_days.textChanged.connect(
            lambda word, field="log_keep_files_days": self.change_setting(
                field, word, setting_type=field, type="int"
            )
        )
        self.textEdit_google_api_key.setReadOnly(True)
        self.google_auth_api_key_paste_btn.clicked.connect(self.google_auth_paste_text)
        # self.textEdit_google_api_key.textChanged.connect(
        #     lambda field="google_api": self.textEdit_change_secure_setting(
        #         field, self.textEdit_google_api_key
        #     )
        # )

    def textEdit_change_secure_setting(self, field, text_edit):
        self.google_api_key = text_edit.toPlainText()
        self.change_secure_setting(field, self.google_api_key, setting_type=field)

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
                "",
                self.lineEdit_apple_note,
                self.label_apple_note_verfied,
                self.label_apple_note_verify_btn,
                setText,
            )

        def google_api():
            self.google_api_key = self.secure_creds.get_creds(
                "english-dict-secure-settings", "google_api"
            )
            self.google_api_key_verified = self.settings.get_value(
                "google_api-verified", False
            )

            self.textEdit_google_api_key.setText(self.google_api_key)
            self.label_google_api_key_verfied.setIcon(
                self.check_icon if self.google_api_key_verified else self.x_icon
            )
            self.label_google_api_key_verify_btn.setDisabled(
                self.google_api_key_verified
            )

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

        def log_file_name():
            self.log_file_name, self.log_file_name_verified = self.get_and_set_settings(
                "log_file_name",
                "file.log",
                self.lineEdit_log_file_name,
                self.label_log_file_name_verfied,
                self.label_log_file_name_verify_btn,
                setText,
            )

        def log_backup_count():
            self.log_backup_count, self.log_backup_count_verified = (
                self.get_and_set_settings(
                    "log_backup_count",
                    5,
                    self.lineEdit_log_backup_count,
                    self.label_log_backup_count_verfied,
                    self.label_log_backup_count_verify_btn,
                    setText,
                    "int",
                )
            )

        def log_file_max_mbs():
            self.log_file_max_mbs, self.log_file_max_mbs_verified = (
                self.get_and_set_settings(
                    "log_file_max_mbs",
                    5,
                    self.lineEdit_log_file_max_mbs,
                    self.label_log_file_max_mbs_verfied,
                    self.label_log_file_max_mbs_verify_btn,
                    setText,
                    "int",
                )
            )

        def log_keep_files_days():
            self.log_keep_files_days, self.log_keep_files_days_verified = (
                self.get_and_set_settings(
                    "log_keep_files_days",
                    5,
                    self.lineEdit_log_keep_files_days,
                    self.label_log_keep_files_days_verfied,
                    self.label_log_keep_files_days_verify_btn,
                    setText,
                    "int",
                )
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
            case "log_file_name":
                log_file_name()
            case "log_backup_count":
                log_backup_count()
            case "log_file_max_mbs":
                log_file_max_mbs()
            case "log_keep_files_days":
                log_keep_files_days()

            case "ALL":
                words_deck()
                model_deck()
                anki_user()
                anki_audio_path()
                apple_note()
                google_api()
                log_file_path()
                log_file_name()
                log_backup_count()
                log_file_max_mbs()
                log_keep_files_days()
        self.settings.end_group()

    def get_and_set_settings(
        self,
        key,
        default,
        lineEdit,
        verify_icon_btn,
        verify_btn,
        setText=False,
        type="str",
    ):
        value = self.settings.get_value(key, default)
        verified = self.settings.get_value(f"{key}-verified", False)
        print(key, value, verified)
        if type == "int":
            value = str(value)
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

    def verify_google_api_key(self):
        # self.start_define.setDisabled(True)
        print(WordModel("", "", "test", "", "", "", "", ""))
        self.audio_thread = AudioThread(
            [WordModel("", "", "test", "", "", "", "", "")],
            folder_path="./",
            credential_string=self.google_api_key,
        )

        self.audio_thread.audio_word.connect(self.google_api_key_response)
        self.audio_thread.error_word.connect(self.google_api_key_response)
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)

        # self.audio_thread.finished.connect(self.reset_thread_reference)

        self.audio_thread.start()

    def google_api_key_response(self, response):
        print()
        success = response.status == Status.AUDIO
        self.response_update(
            [f"{self.google_api_key if success else False}"],
            "google_api",
            self.google_api_key,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_verified,
            "google_api",
        )

        if success:
            paths = [response.audio_path]
            self.removal_thread = QThread(self)
            self.removal_worker = RemoveDuplicateAudio(paths)
            self.removal_worker.moveToThread(self.removal_thread)
            self.removal_thread.started.connect(self.removal_worker.do_work)
            self.removal_thread.finished.connect(self.removal_worker.deleteLater)
            self.removal_thread.finished.connect(self.removal_thread.deleteLater)
            self.removal_thread.start()

    def change_setting(
        self, field, value, verified=False, setting_type="ALL", type="str"
    ):
        print(field, value)
        self.settings.begin_group("settings")
        if type == "int":
            value = int(value if value else 0)
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
        type="str",
    ):
        print("a", value, response)
        if value in response:
            print("b")
            self.change_setting(key, value, True, setting_type, type)
            icon_label.setIcon(self.check_icon)
            verify_btn.setDisabled(True)
            model_verified = True
            self.send_settings_update(key)
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
        print("ss", isExist)
        self.response_update(
            [f"{folder if isExist else False}"],
            "log_file_path",
            folder,
            self.label_log_file_path_verfied,
            self.label_log_file_path_verify_btn,
            self.log_file_path_verified,
            "log_file_path",
        )

    def verify_log_file_name(self):
        self.response_update(
            [self.log_file_name],
            "log_file_name",
            self.log_file_name,
            self.label_log_file_name_verfied,
            self.label_log_file_name_verify_btn,
            self.log_file_name_verified,
            "log_file_name",
        )

    def verify_log_backup_count(self):
        self.response_update(
            [self.log_backup_count],
            "log_backup_count",
            self.log_backup_count,
            self.label_log_backup_count_verfied,
            self.label_log_backup_count_verify_btn,
            self.log_backup_count_verified,
            "log_backup_count",
            "int",
        )

    def verify_log_file_max_mbs(self):
        self.response_update(
            [self.log_file_max_mbs],
            "log_file_max_mbs",
            self.log_file_max_mbs,
            self.label_log_file_max_mbs_verfied,
            self.label_log_file_max_mbs_verify_btn,
            self.log_file_max_mbs_verified,
            "log_file_max_mbs",
            "int",
        )

    def verify_log_keep_files_days(self):
        self.response_update(
            [self.log_keep_files_days],
            "log_keep_files_days",
            self.log_keep_files_days,
            self.label_log_keep_files_days_verfied,
            self.label_log_keep_files_days_verify_btn,
            self.log_keep_files_days_verified,
            "log_keep_files_days",
            "int",
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
        last_row = self.settings_grid_layout.count() // self.columns
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)

        label = QLabel(label_text)
        label.setMinimumWidth(143)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        verify_icon_button = QPushButton()
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_button = QPushButton(verify_button_text)
        verify_button.setCursor(Qt.PointingHandCursor)

        self.settings_grid_layout.addWidget(label, last_row, 0, Qt.AlignTop)

        if folder_icon:
            folder_icon_button = QPushButton()
            folder_icon_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            folder_icon_button.setStyleSheet(
                "background:transparent;border: none; margin: 0px; padding: 0px;"
            )

            folder_icon_button.setCursor(Qt.PointingHandCursor)

            folder_icon_button.setIcon(self.folder_icon)

        if lineEdit:
            line_edit_field = QLineEdit()

            h_layout.addWidget(line_edit_field)
            if folder_icon:
                h_layout.addWidget(folder_icon_button)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
        else:

            h_layout = QVBoxLayout()
            text_edit_field = QTextEdit()

            h_layout.addWidget(text_edit_field)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)

        self.settings_grid_layout.addWidget(
            verify_icon_button, last_row, 2, Qt.AlignTop
        )
        self.settings_grid_layout.addWidget(verify_button, last_row, 3, Qt.AlignTop)

        if folder_icon:
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
            folder = folder if folder[-1] == "/" else folder + "/"
            input_field.blockSignals(True)
            input_field.setText(folder)
            input_field.blockSignals(False)
            self.folder_submit.emit(key, folder)

    def google_auth_paste_text(self):
        """Handle pasting only."""
        print("here")
        clipboard = QApplication.clipboard()
        self.textEdit_google_api_key.setText(clipboard.text())
        self.textEdit_change_secure_setting("google_api", self.textEdit_google_api_key)

    def send_settings_update(self, key):

        # Import Page settings
        if key in ["apple_note"]:
            self.send_import_page_settings()
        if key in ["audio_path", "google_api"]:
            self.send_audio_page_settings()
        if key in ["words", "models"]:
            self.send_sync_page_settings()
        if key in [
            "log_file_path",
            "log_file_name",
            "log_backup_count",
            "log_file_max_mbs",
            "log_keep_files_days",
        ]:
            self.send_logs_page_setting()

    def send_import_page_settings(self):
        self.import_page_settings.emit(self.apple_note, self.apple_note_verified)

    def send_audio_page_settings(self):
        self.audio_page_settings.emit(
            self.google_api_key,
            self.google_api_key_verified,
            self.anki_audio,
            self.anki_audio_verified,
        )

    def send_sync_page_settings(self):
        self.sync_page_settings.emit(
            self.words_deck, self.words_verified, self.model_deck, self.model_verified
        )

    def send_logs_page_setting(self):
        self.log_page_settings.emit(
            self.log_file_path,
            self.log_file_path_verified,
            self.log_file_name,
            self.log_file_name_verified,
        )
        self.save_log_settings_model.emit(
            self.log_file_path,
            self.log_file_name,
            self.log_file_max_mbs,
            self.log_backup_count,
            self.log_keep_files_days,
            False,
        )

    @Slot()
    def send_all_settings(self):
        print("send all settings")
        self.send_import_page_settings()
        self.send_audio_page_settings()
        self.send_sync_page_settings()
        self.send_logs_page_setting()
