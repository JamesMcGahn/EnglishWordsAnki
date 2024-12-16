import os

from PySide6.QtCore import QRect, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPainter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from services.network import NetworkWorker
from services.settings import AppSettings


class SettingsPage(QWidget):

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

        hspacer = QSpacerItem(400, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.settings_page_layout.addItem(hspacer)

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

        self.settings_page_layout.addLayout(self.anki_words_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_model_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_user_hlayout)
        self.settings_page_layout.addItem(vspacer)

        self.settings = AppSettings()
        self.get_settings()

        self.label_anki_words_verify_btn.clicked.connect(self.verify_deck_name)
        self.label_anki_model_verify_btn.clicked.connect(self.verify_deck_model)
        self.label_anki_user_verify_btn.clicked.connect(self.verify_anki_user)
        self.lineEdit_anki_words_deck.textChanged.connect(
            lambda word, field="words": self.change_setting(
                field,
                word,
            )
        )
        self.lineEdit_anki_model_deck.textChanged.connect(
            lambda word, field="model": self.change_setting(
                field,
                word,
            )
        )
        self.lineEdit_anki_user.textChanged.connect(
            lambda word, field="user": self.change_setting(
                field,
                word,
            )
        )

        home_directory = os.path.expanduser("~")
        print("home", home_directory)

    def get_settings(self):
        self.settings.begin_group("settings")
        self.words_deck = self.settings.get_value("words", "")
        self.model_deck = self.settings.get_value("model", "")
        self.anki_user = self.settings.get_value("user", "User 1")
        self.words_verified = self.settings.get_value("words-verified", False)
        self.model_verified = self.settings.get_value("model-verified", False)
        self.anki_user_verified = self.settings.get_value("user-verified", False)
        self.lineEdit_anki_words_deck.setText(self.words_deck)
        self.lineEdit_anki_model_deck.setText(self.model_deck)
        self.lineEdit_anki_user.setText(self.anki_user)
        self.label_anki_words_deck_verfied.setIcon(
            self.check_icon if self.words_verified else self.x_icon
        )
        self.label_anki_model_deck_verfied.setIcon(
            self.check_icon if self.model_verified else self.x_icon
        )
        self.label_anki_user_verfied.setIcon(
            self.check_icon if self.anki_user_verified else self.x_icon
        )
        self.label_anki_words_verify_btn.setDisabled(self.words_verified)
        self.label_anki_model_verify_btn.setDisabled(self.model_verified)
        self.label_anki_user_verify_btn.setDisabled(self.anki_user_verified)
        self.settings.end_group()

    def run_network_check(
        self, task_id, url, json_data, success_callback, error_callback, btn
    ):
        network_thread = QThread(self)

        worker = NetworkWorker(url, json=json_data)
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

    def change_setting(self, field, value, verified=False):
        print(field, value)
        self.settings.begin_group("settings")
        self.settings.set_value(field, value)
        self.settings.set_value(f"{field}-verified", verified)
        self.settings.end_group()
        self.get_settings()

    def deck_response(self, response):
        res = response["result"]
        print(res)
        if self.words_deck in res:
            self.change_setting("words", self.words_deck, True)
            self.label_anki_words_deck_verfied.setIcon(self.check_icon)
            self.label_anki_words_verify_btn.setDisabled(True)
            self.words_verified = True
        else:
            self.label_anki_words_verify_btn.setDisabled(False)
        self.label_anki_words_deck_verfied.setIcon(
            self.check_icon if self.words_verified else self.x_icon
        )

    def model_response(self, response):
        res = response["result"]
        print(res)
        if self.model_deck in res:
            self.change_setting("model", self.model_deck, True)
            self.label_anki_model_deck_verfied.setIcon(self.check_icon)
            self.label_anki_model_verify_btn.setDisabled(True)
            self.model_verified = True
        else:
            self.label_anki_model_verify_btn.setDisabled(False)
        self.label_anki_model_deck_verfied.setIcon(
            self.check_icon if self.model_verified else self.x_icon
        )

    def user_response(self, response):
        res = response["result"]
        print(res)
        if self.anki_user in res:
            self.change_setting("user", self.anki_user, True)
            self.label_anki_user_verfied.setIcon(self.check_icon)
            self.label_anki_model_verify_btn.setDisabled(True)
            self.model_verified = True
        else:
            self.label_anki_model_verify_btn.setDisabled(False)
        self.label_anki_user_verfied.setIcon(
            self.check_icon if self.model_verified else self.x_icon
        )

    def create_input_fields(self, label_text, verify_button_text):
        label = QLabel(label_text)
        label.setMinimumWidth(143)
        line_edit_field = QLineEdit()
        line_edit_field.setMaximumWidth(230)
        verify_icon_button = QPushButton()
        verify_icon_button.setMaximumWidth(40)
        verify_icon_button.setStyleSheet("background:transparent;border: none;")
        verify_button = QPushButton(verify_button_text)
        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)
        h_layout.addWidget(label)
        h_layout.addWidget(line_edit_field)
        h_layout.addWidget(verify_icon_button)
        h_layout.addWidget(verify_button)
        return line_edit_field, verify_icon_button, verify_button, h_layout