from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
)

from models import AppSettingsModel


class SettingsPageInputFactory(QObject):
    """Creates input fields and layouts for settings page"""

    def __init__(self, settings_grid, columns):
        super().__init__()

        self.columns = columns
        self.settings_grid_layout = settings_grid
        self.app_settings = AppSettingsModel()
        self.app_settings.get_settings()
        self._x_icon = QIcon()
        self._x_icon.addFile(
            ":/images/red_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self._check_icon = QIcon()
        self._check_icon.addFile(
            ":/images/green_check.png",
            QSize(),
            QIcon.Mode.Normal,
        )
        self._folder_icon = QIcon()
        self._folder_icon.addFile(
            ":/images/open_folder_on.png",
            QSize(),
            QIcon.Mode.Normal,
        )

    @property
    def x_icon(self):
        return self._x_icon

    @property
    def check_icon(self):
        return self._check_icon

    @property
    def folder_icon(self):
        return self._folder_icon

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
