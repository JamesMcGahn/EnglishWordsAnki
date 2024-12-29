import os

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)

from base import QWidgetBase
from core import AppleNoteImport, AudioThread, RemoveDuplicateAudio
from models import AppSettingsModel, LogSettingsModel, Status, WordModel
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials

from .sp_input_factory import SettingsPageInputFactory


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
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hspacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.settings_page_layout.addItem(self.hspacer)

        # self.settings_page_layout.addItem(hspacer)
        self.settings_grid_layout = QGridLayout()
        self.sp_input_factory = SettingsPageInputFactory(self.settings_grid_layout, 4)
        self.settings_page_layout.addLayout(self.settings_grid_layout)
        self.check_icon = self.sp_input_factory.check_icon
        self.x_icon = self.sp_input_factory.x_icon
        self.folder_icon = self.sp_input_factory.folder_icon

        self.columns = 4

        self.settings_page_layout.addItem(self.hspacer1)
        (
            self.lineEdit_apple_note,
            self.label_apple_note_verfied,
            self.label_apple_note_verify_btn,
            self.apple_note_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "apple_note_name", "Apple Note Name:", "Verify Apple Note"
        )
        (
            self.lineEdit_anki_words_deck,
            self.label_anki_words_deck_verfied,
            self.label_anki_words_verify_btn,
            self.anki_words_deck_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "anki_deck_name", "Word's Deck Name:", "Verify Deck"
        )

        (
            self.lineEdit_anki_model_deck,
            self.label_anki_model_deck_verfied,
            self.label_anki_model_verify_btn,
            self.anki_model_deck_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "anki_model_name", "Word's Model Name:", "Verify Model"
        )

        (
            self.lineEdit_anki_user,
            self.label_anki_user_verfied,
            self.label_anki_user_verify_btn,
            self.anki_user_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "anki_user", "Anki User Name:", "Verify User"
        )
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_path_hlayout,
            self.anki_audio_path_folder_btn,
        ) = self.sp_input_factory.create_input_fields(
            "anki_audio_path", "Anki Audio path:", "Verify Audio Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_path,
            self.label_log_file_path_verfied,
            self.label_log_file_path_verify_btn,
            self.log_file_path_hlayout,
            self.log_file_path_folder_btn,
        ) = self.sp_input_factory.create_input_fields(
            "log_file_path", "Log File path:", "Verify Log Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_name,
            self.label_log_file_name_verfied,
            self.label_log_file_name_verify_btn,
            self.log_file_name_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "log_file_name", "Log File Name:", "Save Log File Name"
        )
        (
            self.lineEdit_log_backup_count,
            self.label_log_backup_count_verfied,
            self.label_log_backup_count_verify_btn,
            self.log_backup_count_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "log_backup_count", "Log Backup Count:", "Save Log Backup Count"
        )
        (
            self.lineEdit_log_file_max_mbs,
            self.label_log_file_max_mbs_verfied,
            self.label_log_file_max_mbs_verify_btn,
            self.log_file_max_mbs_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "log_file_max_mbs", "Log File Max Mbs:", "Save Log File Max Mbs"
        )
        (
            self.lineEdit_log_keep_files_days,
            self.label_log_keep_files_days_verfied,
            self.label_log_keep_files_days_verify_btn,
            self.log_keep_files_days_hlayout,
        ) = self.sp_input_factory.create_input_fields(
            "log_keep_files_days", "Keep Log File Days:", "Save Log File Days"
        )
        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verfied,
            self.label_google_api_key_verify_btn,
            self.google_api_key_vlayout,
        ) = self.sp_input_factory.create_input_fields(
            "google_api_key", "Google Service:", "Verify Google Service", False
        )
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
        # self.get_settings("ALL", setText=True)

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
            lambda: self.open_folder_dialog(
                "anki_audio_path", self.lineEdit_anki_audio_path
            )
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
            lambda: self.open_folder_dialog(
                "anki_audio_path", self.lineEdit_anki_audio_path
            )
        )
        self.lineEdit_apple_note.textChanged.connect(
            lambda word, field="apple_note_name", icon_label=self.label_apple_note_verfied, verify_btn=self.label_apple_note_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_anki_words_deck.textChanged.connect(
            lambda word, field="anki_deck_name", icon_label=self.label_anki_words_deck_verfied, verify_btn=self.label_anki_words_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_anki_model_deck.textChanged.connect(
            lambda word, field="anki_model_name", icon_label=self.label_anki_model_deck_verfied, verify_btn=self.label_anki_model_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_anki_user.textChanged.connect(
            lambda word, field="anki_user", icon_label=self.label_anki_user_verfied, verify_btn=self.label_anki_user_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_anki_audio_path.textChanged.connect(
            lambda word, field="anki_audio_path", icon_label=self.label_anki_audio_path_verfied, verify_btn=self.label_anki_audio_path_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_log_file_path.textChanged.connect(
            lambda word, field="log_file_path", icon_label=self.label_log_file_path_verfied, verify_btn=self.label_log_file_path_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_log_file_name.textChanged.connect(
            lambda word, field="log_file_name", icon_label=self.label_log_file_path_verfied, verify_btn=self.label_log_file_name_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn
            )
        )
        self.lineEdit_log_backup_count.textChanged.connect(
            lambda word, field="log_backup_count", icon_label=self.label_log_backup_count_verfied, verify_btn=self.label_log_backup_count_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn, type="int"
            )
        )
        self.lineEdit_log_file_max_mbs.textChanged.connect(
            lambda word, field="log_file_max_mbs", icon_label=self.label_log_file_max_mbs_verfied, verify_btn=self.label_log_file_max_mbs_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn, type="int"
            )
        )
        self.lineEdit_log_keep_files_days.textChanged.connect(
            lambda word, field="log_keep_files_days", icon_label=self.label_log_keep_files_days_verfied, verify_btn=self.label_log_keep_files_days_verify_btn: self.handle_setting_change(
                field, word, icon_label, verify_btn, type="int"
            )
        )
        self.textEdit_google_api_key.setReadOnly(True)
        self.google_auth_api_key_paste_btn.clicked.connect(self.google_auth_paste_text)
        # self.textEdit_google_api_key.textChanged.connect(
        #     lambda field="google_api": self.textEdit_change_secure_setting(
        #         field, self.textEdit_google_api_key
        #     )
        # )

    def handle_setting_change(self, field, word, icon_label, verify_btn, type="str"):
        """
        Handles the setting change: saves the new value and updates the icon.

        Args:
            field (str): The field name for the setting.
            word (str): The new value of the setting.
            icon_label (QLabel): The icon label to update.
        """
        print(field, word)
        self.settings_model.change_setting(field, word, type=type)
        self.sp_input_factory.change_icon_button(icon_label)
        if verify_btn.isEnabled():
            verify_btn.setDisabled(False)

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
        self.apple_note_thread.finished.connect(self.apple_note_thread.deleteLater)
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
            credential_string=self.textEdit_google_api_key.toPlainText(),
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
            [f"{self.textEdit_google_api_key.toPlainText() if success else False}"],
            "google_api_key",
            self.textEdit_google_api_key.toPlainText(),
            self.label_google_api_key_verfied,
            self.label_google_api_key_verify_btn,
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

    def response_update(
        self,
        response,
        key,
        value,
        icon_label,
        verify_btn,
        type="str",
    ):
        print("a", value, response)
        if value in response:
            print("b")
            self.settings_model.change_setting(key, value, True, type)
            icon_label.setIcon(self.check_icon)
            verify_btn.setDisabled(True)

            self.send_settings_update(key)
        else:
            verify_btn.setDisabled(False)
            icon_label.setIcon(self.x_icon)

    @Slot(str, str)
    def folder_change(self, key, folder):
        if key == "log_file_path":
            self.verify_log_file_path(folder)
        elif key == "anki_audio_path":
            self.verify_anki_user_audio_path(folder)

    def verify_anki_user_audio_path(self, folder):
        isExist = os.path.exists(folder)
        self.response_update(
            [f"{folder if isExist else False}"],
            "anki_audio_path",
            folder,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
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
        )

    def verify_log_file_name(self):
        self.response_update(
            [self.lineEdit_log_file_name.text()],
            "log_file_name",
            self.lineEdit_log_file_name.text(),
            self.label_log_file_name_verfied,
            self.label_log_file_name_verify_btn,
        )

    def verify_log_backup_count(self):
        self.response_update(
            [self.lineEdit_log_backup_count.text()],
            "log_backup_count",
            self.lineEdit_log_backup_count.text(),
            self.label_log_backup_count_verfied,
            self.label_log_backup_count_verify_btn,
            "int",
        )

    def verify_log_file_max_mbs(self):
        self.response_update(
            [self.lineEdit_log_file_max_mbs.text()],
            "log_file_max_mbs",
            self.lineEdit_log_file_max_mbs.text(),
            self.label_log_file_max_mbs_verfied,
            self.label_log_file_max_mbs_verify_btn,
            "int",
        )

    def verify_log_keep_files_days(self):
        self.response_update(
            [self.lineEdit_log_keep_files_days.text()],
            "log_keep_files_days",
            self.lineEdit_log_keep_files_days.text(),
            self.label_log_keep_files_days_verfied,
            self.label_log_keep_files_days_verify_btn,
            "int",
        )

    def apple_note_response(self, response):
        self.response_update(
            [f"{self.lineEdit_apple_note.text() if response else False}"],
            "apple_note_name",
            self.lineEdit_apple_note.text(),
            self.label_apple_note_verfied,
            self.label_apple_note_verify_btn,
        )

    def deck_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "anki_deck_name",
            self.lineEdit_anki_words_deck.text(),
            self.label_anki_words_deck_verfied,
            self.label_anki_words_verify_btn,
        )

    def model_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "anki_model_name",
            self.lineEdit_anki_model_deck.text(),
            self.label_anki_model_deck_verfied,
            self.label_anki_model_verify_btn,
        )

    def user_response(self, response):
        res = response["result"]
        print(res)
        self.response_update(
            res,
            "anki_user",
            self.lineEdit_anki_user.text(),
            self.label_anki_user_verfied,
            self.label_anki_user_verify_btn,
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
        text = clipboard.text()
        self.textEdit_google_api_key.setText(text)
        self.settings_model.change_secure_setting("google_api_key", text)

    def send_settings_update(self, key):

        # Import Page settings
        if key in ["apple_note_name"]:
            self.send_import_page_settings()
        if key in ["audio_path", "google_api_key"]:
            self.send_audio_page_settings()
        if key in ["anki_deck_name", "anki_model_name"]:
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
        apple_note_name, ann_verifed = self.settings_model.get_setting(
            "apple_note_name"
        )
        self.import_page_settings.emit(apple_note_name, ann_verifed)

    def send_audio_page_settings(self):
        google_api_key, gak_verifed = self.settings_model.get_setting("google_api_key")
        anki_audio_path, aap_verifed = self.settings_model.get_setting(
            "anki_audio_path"
        )

        self.audio_page_settings.emit(
            google_api_key,
            gak_verifed,
            anki_audio_path,
            aap_verifed,
        )

    def send_sync_page_settings(self):
        anki_deck_name, adn_verifed = self.settings_model.get_setting("anki_deck_name")
        anki_model_name, amn_verifed = self.settings_model.get_setting(
            "anki_model_name"
        )

        self.sync_page_settings.emit(
            anki_deck_name, adn_verifed, anki_model_name, amn_verifed
        )

    def send_logs_page_setting(self):
        log_file_path, lfp_verifed = self.settings_model.get_setting("log_file_path")
        log_file_name, lfn_verifed = self.settings_model.get_setting("log_file_name")
        log_file_max_mbs, _ = self.settings_model.get_setting("log_file_max_mbs")
        log_backup_count, _ = self.settings_model.get_setting("log_backup_count")
        log_keep_files_days, _ = self.settings_model.get_setting("log_keep_files_days")

        self.log_page_settings.emit(
            log_file_path,
            lfp_verifed,
            log_file_name,
            lfn_verifed,
        )
        self.save_log_settings_model.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            False,
        )

    @Slot()
    def send_all_settings(self):
        print("send all settings")
        self.send_import_page_settings()
        self.send_audio_page_settings()
        self.send_sync_page_settings()
        self.send_logs_page_setting()
