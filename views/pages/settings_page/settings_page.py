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
        (
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_path_hlayout,
        ) = self.create_input_fields("Anki Audio path:", "Verify Audio Path")

        self.settings_page_layout.addLayout(self.anki_words_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_model_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_user_hlayout)
        self.settings_page_layout.addLayout(self.anki_audio_path_hlayout)
        self.settings_page_layout.addItem(vspacer)

        self.settings = AppSettings()
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        self.get_settings()

        self.label_anki_words_verify_btn.clicked.connect(self.verify_deck_name)
        self.label_anki_model_verify_btn.clicked.connect(self.verify_deck_model)
        self.label_anki_user_verify_btn.clicked.connect(self.verify_anki_user)
        self.label_anki_audio_path_verify_btn.clicked.connect(
            self.verify_anki_user_audio_path
        )
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
        self.lineEdit_anki_audio_path.textChanged.connect(
            lambda word, field="audio": self.change_setting(
                field,
                word,
            )
        )

    def get_settings(self):
        self.settings.begin_group("settings")
        self.words_deck, self.words_verified = self.get_and_set_settings(
            "words",
            "",
            self.lineEdit_anki_words_deck,
            self.label_anki_words_deck_verfied,
            self.label_anki_words_verify_btn,
        )
        self.model_deck, self.model_verified = self.get_and_set_settings(
            "model",
            "",
            self.lineEdit_anki_model_deck,
            self.label_anki_model_deck_verfied,
            self.label_anki_model_verify_btn,
        )
        self.anki_user, self.anki_user_verified = self.get_and_set_settings(
            "user",
            "User 1",
            self.lineEdit_anki_user,
            self.label_anki_user_verfied,
            self.label_anki_user_verify_btn,
        )
        self.anki_audio, self.anki_audio_verified = self.get_and_set_settings(
            "audio",
            f"{self.home_directory}/Library/Application Support/Anki2/{self.anki_user}/collection.media",
            self.lineEdit_anki_audio_path,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
        )
        self.settings.end_group()

    def get_and_set_settings(self, key, default, lineEdit, verify_icon_btn, verify_btn):
        value = self.settings.get_value(key, default)
        verified = self.settings.get_value(f"{key}-verified", False)
        lineEdit.setText(value)
        verify_icon_btn.setIcon(self.check_icon if verified else self.x_icon)
        verify_btn.setDisabled(verified)
        return value, verified

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

    def response_update(
        self, response, key, value, icon_label, verify_btn, model_verified
    ):
        if value in response:
            self.change_setting(key, value, True)
            icon_label.setIcon(self.check_icon)
            verify_btn.setDisabled(True)
            model_verified = True
        else:
            verify_btn.setDisabled(False)
            icon_label.setIcon(self.check_icon if model_verified else self.x_icon)

    def verify_anki_user_audio_path(self):
        isExist = os.path.exists(self.anki_audio)
        self.response_update(
            [f"{self.anki_audio if isExist else False}"],
            "audio",
            self.anki_audio,
            self.label_anki_audio_path_verfied,
            self.label_anki_audio_path_verify_btn,
            self.anki_audio_verified,
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
