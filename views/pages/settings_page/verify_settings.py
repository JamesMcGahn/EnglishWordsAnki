import os

from PySide6.QtCore import QThread, Signal

from base import QWidgetBase
from core import AppleNoteImport, AudioThread, RemoveDuplicateAudio
from models import AppSettingsModel, LogSettingsModel, Status, WordModel
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials

from .settings_page_view import SettingsPageView


class VerifySettings(QWidgetBase):
    send_settings_verified = Signal(str)
    verify_response_update_ui = Signal(str, bool)
    send_settings_update = Signal(str)
    change_verify_btn_disable = Signal(str, bool)

    def __init__(self):
        super().__init__()

        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.secure_creds = SecureCredentials()
        self.view = SettingsPageView()
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)

    def verify_settings(self, key, value=None):
        if key == "apple_note_name":
            self._verify_apple_note_name()
        elif key == "anki_deck_name":
            self._verify_deck_name()
        elif key == "anki_model_name":
            self._verify_deck_model()
        elif key == "anki_user":
            self._verify_anki_user()
        elif key == "google_api_key":
            self._verify_google_api_key()
        elif key == "anki_audio_path":
            self._verify_path_keys("anki_audio_path", value)
        elif key == "log_file_path":
            self._verify_path_keys("log_file_path", value)
        elif key == "log_backup_count":
            text = self.view.get_line_edit_text("log_backup_count")
            self.update_ui_verified("log_backup_count", text, "int")
        elif key == "log_file_name":
            text = self.view.get_line_edit_text("log_file_name")
            if not text.endswith(".log"):
                text = text + ".log"
            self.update_ui_verified("log_file_name", text)
        elif key == "log_file_max_mbs":
            text = self.view.get_line_edit_text("log_file_max_mbs")
            self.update_ui_verified("log_file_max_mbs", text, "int")
        elif key == "log_keep_files_days":
            text = self.view.get_line_edit_text("log_keep_files_days")
            self.update_ui_verified("log_keep_files_days", text, "int")
        elif key == "dictionary_source":
            text = self.view.get_combo_box_text("dictionary_source")
            self.update_ui_verified("dictionary_source", text)
        elif key == "merriam_webster_api_key":
            self._verify_merriam_webster_api_key()

    def update_ui_verified(self, key, value, type="str"):
        self.settings_model.change_setting(key, value, True, type)
        self.verify_response_update_ui.emit(key, True)
        self.send_settings_update.emit(key)

    def run_network_check(self, key, url, json_data, success_cb=None, error_cb=None):
        network_thread = QThread()

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
        network_thread.finished.connect(lambda: self.cleanup_task(key, True))
        self.running_tasks[key] = (network_thread, worker)
        self.change_verify_btn_disable.emit(key, False)
        network_thread.start()

    def cleanup_task(self, task_id, thread_finished=False):
        if task_id in self.running_tasks:
            if thread_finished:
                w_thread, worker = self.running_tasks.pop(task_id)
                w_thread.deleteLater()
                print(f"Task {task_id} - Thread deleting.")
            else:
                w_thread, worker = self.running_tasks[task_id]
                worker.deleteLater()
                w_thread.quit()
                print(f"Task {task_id} - Worker cleaned up. Thread quitting.")

    def _verify_apple_note_name(self):
        self.change_verify_btn_disable.emit("apple_note_name", False)
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

    def _verify_deck_name(self):
        json_data = {"action": "deckNames", "version": 6}
        self.run_network_check(
            "anki_deck_name",
            "http://127.0.0.1:8765/",
            json_data,
            self.deck_response,
        )

    def _verify_deck_model(self):
        json_data = {"action": "modelNames", "version": 6}
        self.run_network_check(
            "anki_model_name",
            "http://127.0.0.1:8765/",
            json_data,
            self.model_response,
        )

    def _verify_anki_user(self):
        json_data = {"action": "getProfiles", "version": 6}
        self.run_network_check(
            "anki_user",
            "http://127.0.0.1:8765/",
            json_data,
            self.user_response,
        )

    def _verify_google_api_key(self):
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

    def _verify_merriam_webster_api_key(self):
        key = self.view.get_line_edit_text("merriam_webster_api_key")
        print(key, "key")
        self.run_network_check(
            "merriam_webster_api_key",
            f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/voluminous?key={key}",
            None,
            self.merriam_webster_response,
        )

    def _verify_path_keys(self, key, folder):

        isExist = os.path.exists(folder)
        if isExist:
            self.update_ui_verified(key, folder)

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
            self.update_ui_verified(key, value)
        else:
            self.verify_response_update_ui.emit(key, False)

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

    def merriam_webster_response(self, _):
        text = self.view.get_line_edit_text("merriam_webster_api_key")
        self.update_ui_verified("merriam_webster_api_key", text)
