import os

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWidgetBase
from models import AppSettingsModel, LogSettingsModel
from services.settings import AppSettings, SecureCredentials

from .settings_page_view import SettingsPageView
from .verify_settings import VerifySettings


class SettingsPage(QWidgetBase):

    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    define_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)
    verify_response_update_ui = Signal(str, bool)
    handle_change_update_ui = Signal(str)
    change_verify_btn_disable = Signal(str, bool)

    def __init__(self):
        super().__init__()

        self.view = SettingsPageView()
        self.setLayout(self.view.layout())
        self.verify_settings = VerifySettings()
        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.secure_creds = SecureCredentials()
        self.timers = {}
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)

        self.save_log_settings_model.connect(self.log_settings.save_log_settings)

        self.view.btn_apple_note_name_verify.clicked.connect(
            lambda: self.handle_verify("apple_note_name")
        )
        self.view.btn_anki_deck_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_deck_name")
        )
        self.view.btn_anki_model_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_model_name")
        )
        self.view.btn_anki_user_verify.clicked.connect(
            lambda: self.handle_verify("anki_user")
        )
        self.view.btn_google_api_key_verify.clicked.connect(
            lambda: self.handle_verify("google_api_key")
        )
        self.view.btn_log_file_name_verify.clicked.connect(
            lambda: self.handle_verify("log_file_name")
        )
        self.view.btn_log_backup_count_verify.clicked.connect(
            lambda: self.handle_verify("log_backup_count")
        )
        self.view.btn_log_file_max_mbs_verify.clicked.connect(
            lambda: self.handle_verify("log_file_max_mbs")
        )
        self.view.btn_log_keep_files_days_verify.clicked.connect(
            lambda: self.handle_verify("log_keep_files_days")
        )
        self.view.btn_dictionary_source_verify.clicked.connect(
            lambda: self.handle_verify("dictionary_source")
        )
        self.view.btn_merriam_webster_api_key_verify.clicked.connect(
            lambda: self.handle_verify("merriam_webster_api_key")
        )

        self.view.comboBox_dictionary_source.currentIndexChanged.connect(
            lambda index, sender=self.view.comboBox_dictionary_source, key="dictionary_source": self.onComboBox_changed(
                index, sender, key
            )
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
        self.view.lineEdit_merriam_webster_api_key.textChanged.connect(
            lambda text, key="merriam_webster_api_key", field=self.view.lineEdit_merriam_webster_api_key: self.handle_secure_text_change_timer(
                text, key, field
            )
        )
        self.setup_text_changed_connections()
        self.verify_settings.verify_response_update_ui.connect(
            self.view.verify_response_update
        )
        self.verify_settings.send_settings_update.connect(self.send_settings_update)
        self.handle_change_update_ui.connect(self.view.handle_setting_change_update)
        self.verify_settings.change_verify_btn_disable.connect(
            self.view.set_verify_btn_disable
        )
        self.view.folder_submit.connect(self.folder_change)
        self.view.secure_setting_change.connect(self.handle_secure_setting_change)

    def setup_text_changed_connections(self):
        for item in self.line_edit_connections:
            line_edit, field, field_type = item
            line_edit.textChanged.connect(
                lambda word, field=field, type=field_type: self.handle_setting_change(
                    field, word, type=type
                )
            )

    def handle_secure_text_change_timer(self, text, key, field):
        if key not in self.timers:
            self.timers[key] = QTimer()
            self.timers[key].setSingleShot(True)
            self.timers[key].timeout.connect(
                lambda: self.handle_secure_user_done_typing(key, field)
            )

        self.timers[key].start(1000)

    def handle_secure_user_done_typing(self, key, field):
        text = field.text()
        self.handle_secure_setting_change(key, text)

    def onComboBox_changed(self, index, sender, key):
        selected_text = sender.currentText()
        self.handle_setting_change(key, selected_text)

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

    @Slot(str, str)
    def handle_secure_setting_change(self, field, word):
        self.settings_model.change_secure_setting(
            field,
            word,
        )
        self.handle_change_update_ui.emit(field)

    def handle_verify(self, key):
        self.verify_settings.verify_settings(key)

    @Slot(str, str)
    def folder_change(self, key, folder):
        self.verify_settings.verify_settings(key, folder)

    def send_settings_update(self, key):

        # Import Page settings
        if key in ["apple_note_name"]:
            self.send_import_page_settings()
        elif key in ["audio_path", "google_api_key"]:
            self.send_audio_page_settings()
        elif key in ["anki_deck_name", "anki_model_name"]:
            self.send_sync_page_settings()
        elif key in [
            "log_file_path",
            "log_file_name",
            "log_backup_count",
            "log_file_max_mbs",
            "log_keep_files_days",
        ]:
            self.send_logs_page_setting()
        elif key in ["dictionary_source", "merriam_webster_api_key"]:
            self.send_define_page_settings()

    def send_define_page_settings(self):
        dictionary_source, dict_source_verifed = self.settings_model.get_setting(
            "dictionary_source"
        )
        merriam_webster_api_key, merriam_webster_verifed = (
            self.settings_model.get_setting("merriam_webster_api_key")
        )

        self.define_page_settings.emit(
            dictionary_source,
            dict_source_verifed,
            merriam_webster_api_key,
            merriam_webster_verifed,
        )

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
        self.send_define_page_settings()
