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
        self.label_anki_words_deck = QLabel("Word's Deck Name:")
        self.label_anki_words_deck.setMinimumWidth(143)
        self.lineEdit_anki_words_deck = QLineEdit()
        self.lineEdit_anki_words_deck.setMaximumWidth(230)
        self.label_anki_words_deck_verfied = QPushButton()
        self.label_anki_words_deck_verfied.setMaximumWidth(40)
        self.label_anki_words_deck_verfied.setObjectName("anki_verify_icon_w")
        self.label_anki_words_deck_verfied.setStyleSheet(
            """QPushButton#anki_verify_icon_w{background:transparent;border: none;}"""
        )
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

        self.label_anki_words_verify_btn = QPushButton("Verify Deck")
        self.anki_words_deck_hlayout = QHBoxLayout()
        self.anki_words_deck_hlayout.setSpacing(10)
        # self.anki_words_deck_hlayout.addItem(hspacer)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck)
        self.anki_words_deck_hlayout.addWidget(self.lineEdit_anki_words_deck)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_deck_verfied)
        self.anki_words_deck_hlayout.addWidget(self.label_anki_words_verify_btn)

        hspacer = QSpacerItem(400, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        vspacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # self.settings_page_layout.addItem(hspacer)

        self.label_anki_model_deck = QLabel("Word's Model Name:")
        self.label_anki_model_deck.setMinimumWidth(143)
        self.lineEdit_anki_model_deck = QLineEdit()
        self.lineEdit_anki_model_deck.setMaximumWidth(230)
        self.label_anki_model_deck_verfied = QPushButton()
        self.label_anki_model_deck_verfied.setMaximumWidth(40)
        self.label_anki_model_deck_verfied.setObjectName("anki_verify_icon_w")
        self.label_anki_model_deck_verfied.setStyleSheet(
            """QPushButton#anki_verify_icon_w{background:transparent;border: none;}"""
        )
        self.label_anki_model_verify_btn = QPushButton("Verify Deck")
        self.anki_model_deck_hlayout = QHBoxLayout()
        self.anki_model_deck_hlayout.setSpacing(10)
        # self.anki_model_deck_hlayout.addItem(hspacer)
        self.anki_model_deck_hlayout.addWidget(self.label_anki_model_deck)
        self.anki_model_deck_hlayout.addWidget(self.lineEdit_anki_model_deck)
        self.anki_model_deck_hlayout.addWidget(self.label_anki_model_deck_verfied)
        self.anki_model_deck_hlayout.addWidget(self.label_anki_model_verify_btn)

        self.settings_page_layout.addLayout(self.anki_words_deck_hlayout)
        self.settings_page_layout.addLayout(self.anki_model_deck_hlayout)
        self.settings_page_layout.addItem(vspacer)

        self.settings = AppSettings()
        self.get_settings()

        self.label_anki_words_verify_btn.clicked.connect(self.verify_deck_name)
        self.label_anki_model_verify_btn.clicked.connect(self.verify_deck_model)
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

    def get_settings(self):
        self.settings.begin_group("settings")
        self.words_deck = self.settings.get_value("words", "")
        self.model_deck = self.settings.get_value("model", "")
        self.words_verified = self.settings.get_value("words-verified", False)
        self.model_verified = self.settings.get_value("model-verified", False)
        self.lineEdit_anki_words_deck.setText(self.words_deck)
        self.lineEdit_anki_model_deck.setText(self.model_deck)
        self.label_anki_words_deck_verfied.setIcon(
            self.check_icon if self.words_verified else self.x_icon
        )
        self.label_anki_model_deck_verfied.setIcon(
            self.check_icon if self.model_verified else self.x_icon
        )
        self.label_anki_words_verify_btn.setDisabled(self.words_verified)
        self.label_anki_model_verify_btn.setDisabled(self.model_verified)
        self.settings.end_group()

    def verify_deck_name(self):
        json = {"action": "deckNames", "version": 6}
        self.net_check_deck = QThread(self)

        self.check_deck = NetworkWorker("http://127.0.0.1:8765/", json=json)

        self.check_deck.moveToThread(self.net_check_deck)
        self.check_deck.response.connect(self.deck_response)
        self.net_check_deck.started.connect(self.check_deck.do_work)
        self.net_check_deck.start()
        self.label_anki_words_verify_btn.setDisabled(True)
        self.check_deck.finished.connect(self.check_deck.deleteLater)
        self.net_check_deck.finished.connect(self.net_check_deck.deleteLater)
        self.check_deck.error.connect(
            lambda: self.label_anki_words_verify_btn.setDisabled(False)
        )

    def verify_deck_model(self):
        json = {"action": "modelNames", "version": 6}
        self.net_check_model = QThread(self)

        self.check_model = NetworkWorker("http://127.0.0.1:8765/", json=json)

        self.check_model.moveToThread(self.net_check_model)
        self.check_model.response.connect(self.model_response)
        self.net_check_model.started.connect(self.check_model.do_work)
        self.net_check_model.start()
        self.label_anki_model_verify_btn.setDisabled(True)
        self.check_model.finished.connect(self.check_model.deleteLater)
        self.net_check_model.finished.connect(self.net_check_model.deleteLater)
        self.check_model.error.connect(
            lambda: self.label_anki_model_verify_btn.setDisabled(False)
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
