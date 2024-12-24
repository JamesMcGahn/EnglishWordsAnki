from PySide6.QtCore import QSize, QThread, Signal
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget

from services.logger import Logger
from views.layout import CentralWidget


class MainWindow(QMainWindow):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("Custom MainWindow")
        self.setObjectName("MainWindow")
        self.resize(875, 985)
        self.setMaximumSize(QSize(875, 985))
        font = QFont()
        font.setFamilies([".AppleSystemUIFont"])
        self.setFont(font)

        self.submit_btn = QPushButton("Submit")
        self.qwidget = QWidget()
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.submit_btn)
        self.qwidget.setLayout(self.v_layout)

        # self.setCentralWidget(self.qwidget)

        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)
        self.logger = Logger(turn_off_print=False)
        self.send_logs.connect(self.logger.insert)
        self.centralWidget.send_logs.connect(self.logger.insert)
        self.appshutdown.connect(self.logger.close)
        self.appshutdown.connect(self.centralWidget.notified_app_shutting)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event to emit the shutdown signals and ensure the application closes properly.

        Args:
            event (QCloseEvent): The close event triggered when the user attempts to close the window.

        Returns:
            None: This function does not return a value.
        """
        self.send_logs.emit("Closing Application", "INFO", True)
        self.appshutdown.emit()
        event.accept()
