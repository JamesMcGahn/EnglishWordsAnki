import os

from PySide6.QtCore import QThread, Signal, Slot

from base import QWidgetBase
from core import AppleNoteImport, AudioThread, RemoveDuplicateAudio
from models import AppSettingsModel, LogSettingsModel, Status, WordModel
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials

from .settings_page_view import SettingsPageView


class SettingsPage(QWidgetBase):

    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)
    verify_response_update_ui = Signal(str, bool)
    handle_change_update_ui = Signal(str)
    change_verify_btn_disable = Signal(str, bool)

    def __init__(self):
        super().__init__()

        self.view = SettingsPageView()
        self.setLayout(self.view.layout())

        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.secure_creds = SecureCredentials()

        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)

        self.save_log_settings_model.connect(self.log_settings.save_log_settings)

        self.view.btn_apple_note_name_verify.clicked.connect(
            self.verify_apple_note_name
        )
        self.view.btn_anki_deck_name_verify.clicked.connect(self.verify_deck_name)
        self.view.btn_anki_model_name_verify.clicked.connect(self.verify_deck_model)
        self.view.btn_anki_user_verify.clicked.connect(self.verify_anki_user)
        self.view.btn_google_api_key_verify.clicked.connect(self.verify_google_api_key)
        self.view.btn_log_file_name_verify.clicked.connect(self.verify_log_file_name)
        self.view.btn_log_backup_count_verify.clicked.connect(
            self.verify_log_backup_count
        )
        self.view.btn_log_file_max_mbs_verify.clicked.connect(
            self.verify_log_file_max_mbs
        )
        self.view.btn_log_keep_files_days_verify.clicked.connect(
            self.verify_log_keep_files_days
        )

        self.line_edit_connections = [
            (self.view.lineEdit_apple_note_name, "apple_note_name", "str"),
            (self.view.lineEdit_anki_deck_name, "anki_deck_name", "str"),
            (self.view.lineEdit_anki_model_name, "anki_model_name", "str"),
            (self.view.lineEdit_anki_user, "anki_user", "str"),
            (self.view.lineEdit_anki_audio_path, "anki_audio_path", "str"),
            (self.view.lineEdit_log_file_path, "log_file_path", "str"),
            (self.view.lineEdit_log_file_name, "log_file_name", "str"),
            (self.view.lineEdit_log_backup_count, "log_backup_count", "int"),
            (self.view.lineEdit_log_file_max_mbs, "log_file_max_mbs", "int"),
            (self.view.lineEdit_log_keep_files_days, "log_keep_files_days", "int"),
        ]

        self.setup_text_changed_connections()
        self.verify_response_update_ui.connect(self.view.verify_response_update)
        self.handle_change_update_ui.connect(self.view.handle_setting_change_update)
        self.change_verify_btn_disable.connect(self.view.set_verify_btn_disable)
        self.view.folder_submit.connect(self.folder_change)

    def setup_text_changed_connections(self):
        for item in self.line_edit_connections:
            line_edit, field, field_type = item
            line_edit.textChanged.connect(
                lambda word, field=field, type=field_type: self.handle_setting_change(
                    field, word, type=type
                )
            )

    def handle_setting_change(self, field, word, type="str"):
        """
        Handles the setting change: saves the new value and updates the icon.

        Args:
            field (str): The field name for the setting.
            word (str): The new value of the setting.
            icon_label (QLabel): The icon label to update.
        """
        print(field, word)
        self.settings_model.change_setting(field, word, type=type)
        self.handle_change_update_ui.emit(field)

    def run_network_check(self, key, url, json_data, success_cb=None, error_cb=None):
        network_thread = QThread(self)

        worker = NetworkWorker(url, json=json_data, timeout=25)
        worker.moveToThread(network_thread)

        # Signal-Slot Connections
        worker.response.connect(lambda: self.change_verify_btn_disable.emit(key, True))
        if success_cb:
            worker.response.connect(success_cb)
        if error_cb:
            worker.error.connect(error_cb)
        network_thread.started.connect(worker.do_work)
        worker.finished.connect(lambda: self.cleanup_task(key))
        self.running_tasks[key] = (network_thread, worker)
        self.change_verify_btn_disable.emit(key, False)
        network_thread.start()

    def cleanup_task(self, task_id):
        if task_id in self.running_tasks:
            thread, worker = self.running_tasks.pop(task_id)
            worker.deleteLater()
            thread.quit()
            thread.deleteLater()

            print(f"Task {task_id} cleaned up.")

    def verify_apple_note_name(self):
        # TODO change to signal
        self.change_verify_btn_disable.emit("apple_note_name", False)
        self.view.btn_apple_note_name_verify.setDisabled(False)
        self.apple_note_thread = QThread(self)
        self.apple_worker = AppleNoteImport(
            self.view.get_line_edit_text("apple_note_name")
        )
        self.running_tasks["apple_note_name"] = (
            self.apple_note_thread,
            self.apple_worker,
        )
        self.apple_worker.moveToThread(self.apple_note_thread)
        self.apple_worker.note_name_verified.connect(self.apple_note_response)
        self.apple_worker.finished.connect(lambda: self.cleanup_task("apple_note_name"))
        self.apple_note_thread.started.connect(self.apple_worker.verify_note_name)
        self.apple_note_thread.start()

    def verify_deck_name(self):
        json_data = {"action": "deckNames", "version": 6}
        print("here")
        # TODO change cb to signal
        self.run_network_check(
            "anki_deck_name",
            "http://127.0.0.1:8765/",
            json_data,
            self.deck_response,
        )

    def verify_deck_model(self):
        # TODO change cb to signal
        json_data = {"action": "modelNames", "version": 6}
        self.run_network_check(
            "anki_model_name",
            "http://127.0.0.1:8765/",
            json_data,
            self.model_response,
        )

    def verify_anki_user(self):
        # TODO change cb to signal
        json_data = {"action": "getProfiles", "version": 6}
        self.run_network_check(
            "anki_user",
            "http://127.0.0.1:8765/",
            json_data,
            self.user_response,
        )

    def verify_google_api_key(self):
        # self.start_define.setDisabled(True)
        print(WordModel("", "", "test", "", "", "", "", ""))
        self.audio_thread = AudioThread(
            [WordModel("", "", "test", "", "", "", "", "")],
            folder_path="./",
            credential_string=self.view.get_text_edit_text("google_api_key"),
        )

        self.audio_thread.audio_word.connect(self.google_api_key_response)
        self.audio_thread.error_word.connect(self.google_api_key_response)
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)

        # self.audio_thread.finished.connect(self.reset_thread_reference)

        self.audio_thread.start()

    def google_api_key_response(self, response):
        print()
        success = response.status == Status.AUDIO
        text = self.view.get_text_edit_text("google_api_key")
        self.response_update([f"{text if success else False}"], "google_api_key", text)

        if success:
            paths = [response.audio_path]
            self.removal_thread = QThread(self)
            self.removal_worker = RemoveDuplicateAudio(paths)
            self.removal_worker.moveToThread(self.removal_thread)
            self.removal_thread.started.connect(self.removal_worker.do_work)
            self.removal_thread.finished.connect(self.removal_worker.deleteLater)
            self.removal_thread.finished.connect(self.removal_thread.deleteLater)
            self.removal_thread.start()

    def response_update(self, response, key, value, type="str"):
        print("a", value, response)
        if value in response:
            print("b")
            self.settings_model.change_setting(key, value, True, type)
            self.verify_response_update_ui.emit(key, True)

            self.send_settings_update(key)
        else:
            self.verify_response_update_ui.emit(key, False)

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
        )

    def verify_log_file_path(self, folder):

        isExist = os.path.exists(folder)
        print("ss", isExist)
        self.response_update(
            [f"{folder if isExist else False}"],
            "log_file_path",
            folder,
        )

    def verify_log_file_name(self):
        text = self.view.get_line_edit_text("log_file_name")
        self.response_update([text], "log_file_name", text)

    def verify_log_backup_count(self):
        text = self.view.get_line_edit_text("log_backup_count")
        self.response_update([text], "log_backup_count", text, "int")

    def verify_log_file_max_mbs(self):
        text = self.view.get_line_edit_text("log_file_max_mbs")
        self.response_update([text], "log_file_max_mbs", text, "int")

    def verify_log_keep_files_days(self):
        text = self.view.get_line_edit_text("log_keep_files_days")
        self.response_update([text], "log_keep_files_days", text, "int")

    def apple_note_response(self, response):
        text = self.view.get_line_edit_text("apple_note_name")
        self.response_update(
            [f"{text if response else False}"], "apple_note_name", text
        )

    def deck_response(self, response):
        res = response["result"]
        print(res)
        text = self.view.get_line_edit_text("anki_deck_name")
        self.response_update(res, "anki_deck_name", text)

    def model_response(self, response):
        res = response["result"]
        print(res)
        text = self.view.get_line_edit_text("anki_model_name")
        self.response_update(res, "anki_model_name", text)

    def user_response(self, response):
        res = response["result"]
        print(res)
        text = self.view.get_line_edit_text("anki_user")
        self.response_update(res, "anki_user", text)

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
