from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
)

from base import QWidgetBase
from models import AppSettingsModel


class SettingsPageView(QWidgetBase):
    folder_submit = Signal(str, str)
    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)

    def __init__(self):
        super().__init__()
        self.settings_page_layout = QHBoxLayout(self)

        self.app_settings = AppSettingsModel()
        self.app_settings.get_settings()
        self.inner_settings_page_layout = QHBoxLayout()
        self.settings_page_layout.addLayout(self.inner_settings_page_layout)
        self.vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_page_layout.addItem(self.vspacer)

        self.hspacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hspacer1 = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.settings_page_layout.addItem(self.hspacer)

        # self.settings_page_layout.addItem(hspacer)
        self.settings_grid_layout = QGridLayout()
        self.settings_page_layout.addLayout(self.settings_grid_layout)

        self.columns = 4

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

        self.settings_page_layout.addItem(self.hspacer1)
        (
            self.lineEdit_apple_note_name,
            self.label_apple_note_name_verified_icon,
            self.btn_apple_note_name_verify,
            self.hlayout_apple_note_name,
        ) = self.create_input_fields(
            "apple_note_name", "Apple Note Name:", "Verify Apple Note"
        )
        (
            self.lineEdit_anki_deck_name,
            self.label_anki_deck_name_verified_icon,
            self.btn_anki_deck_name_verify,
            self.hlayout_anki_deck_name,
        ) = self.create_input_fields(
            "anki_deck_name", "Word's Deck Name:", "Verify Deck"
        )

        (
            self.lineEdit_anki_model_name_deck,
            self.label_anki_model_name_verified_icon,
            self.btn_anki_model_name_verify,
            self.hlayout_anki_model_name,
        ) = self.create_input_fields(
            "anki_model_name", "Word's Model Name:", "Verify Model"
        )

        (
            self.lineEdit_anki_user,
            self.label_anki_user_verified_icon,
            self.btn_anki_user_verify,
            self.hlayout_anki_user,
        ) = self.create_input_fields("anki_user", "Anki User Name:", "Verify User")
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verified_icon,
            self.btn_anki_audio_path_verify,
            self.hlayout_anki_audio_path,
            self.btn_anki_audio_path_folder,
        ) = self.create_input_fields(
            "anki_audio_path", "Anki Audio path:", "Verify Audio Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_path,
            self.label_log_file_path_verified_icon,
            self.btn_log_file_path_verify,
            self.hlayout_log_file_path,
            self.btn_log_file_path_folder,
        ) = self.create_input_fields(
            "log_file_path", "Log File path:", "Verify Log Path", folder_icon=True
        )
        (
            self.lineEdit_log_file_name,
            self.label_log_file_name_verified_icon,
            self.btn_log_file_name_verify,
            self.hlayout_log_file_name,
        ) = self.create_input_fields(
            "log_file_name", "Log File Name:", "Save Log File Name"
        )
        (
            self.lineEdit_log_backup_count,
            self.label_log_backup_count_verified_icon,
            self.btn_log_backup_count_verify,
            self.hlayout_log_backup_count,
        ) = self.create_input_fields(
            "log_backup_count", "Log Backup Count:", "Save Log Backup Count"
        )
        (
            self.lineEdit_log_file_max_mbs,
            self.label_log_file_max_mbs_verified_icon,
            self.btn_log_file_max_mbs_verify,
            self.hlayout_log_file_max_mbs,
        ) = self.create_input_fields(
            "log_file_max_mbs", "Log File Max Mbs:", "Save Log File Max Mbs"
        )
        (
            self.lineEdit_log_keep_files_days,
            self.label_log_keep_files_days_verified_icon,
            self.btn_log_keep_files_days_verify,
            self.hlayout_log_keep_files_days,
        ) = self.create_input_fields(
            "log_keep_files_days", "Keep Log File Days:", "Save Log File Days"
        )
        (
            self.textEdit_google_api_key,
            self.label_google_api_key_verified_icon,
            self.btn_google_api_key_verify,
            self.vlayout_google_api_key,
        ) = self.create_input_fields(
            "google_api_key", "Google Service:", "Verify Google Service", False
        )
        self.vspacer2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vspacer3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.settings_grid_layout.addItem(
            self.vspacer2, self.settings_grid_layout.count() // self.columns, 2
        )
        self.google_auth_api_key_paste_btn = QPushButton("Paste API Key")
        self.vlayout_google_api_key.addWidget(self.google_auth_api_key_paste_btn)
        self.settings_page_layout.addItem(self.vspacer3)

        self.textEdit_google_api_key.setReadOnly(True)
        self.google_auth_api_key_paste_btn.clicked.connect(self.google_auth_paste_text)

    def google_auth_paste_text(self):
        """Handle pasting only."""
        print("here")
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        self.textEdit_google_api_key.setText(text)

        # TODO: signal to update settings
        # self.settings_model.change_secure_setting("google_api_key", text)

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

    def create_input_fields(
        self, key, label_text, verify_button_text, lineEdit=True, folder_icon=False
    ):

        value, verified = self.app_settings.get_setting(key)
        last_row = self.settings_grid_layout.count() // self.columns
        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignLeft)

        label = QLabel(label_text)
        label.setMinimumWidth(143)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        verify_icon_button = QPushButton()
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_icon_button.setIcon(self.check_icon if verified else self.x_icon)
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
            line_edit_field.setText(str(value))
            h_layout.addWidget(line_edit_field)
            if folder_icon:
                h_layout.addWidget(folder_icon_button)
            self.settings_grid_layout.addLayout(h_layout, last_row, 1, Qt.AlignTop)
        else:

            h_layout = QVBoxLayout()
            text_edit_field = QTextEdit()
            text_edit_field.setText(value)
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

    def change_icon_button(self, button, verified=False):
        button.setIcon(self.check_icon if verified else self.x_icon)

    @Slot(str, bool)
    def verify_response_update(self, key, verified):
        icon_label = getattr(self, f"label_{key}_verified_icon")
        verify_btn = getattr(self, f"btn_{key}_verify")
        if verified:
            self.change_icon_button(icon_label, True)
            verify_btn.setDisabled(True)
        else:
            self.change_icon_button(icon_label, False)
            verify_btn.setDisabled(False)

    @Slot(str)
    def handle_setting_change_update(self, key):
        icon_label = getattr(self, f"label_{key}_verified_icon")
        self.change_icon_button(icon_label, False)

        verify_btn = getattr(self, f"btn_{key}_verify")
        if verify_btn.isEnabled():
            verify_btn.setDisabled(False)
