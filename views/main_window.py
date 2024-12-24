from PySide6.QtCore import QSize, QThread, Signal
from PySide6.QtGui import QAction, QCloseEvent, QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from services.logger import Logger
from views.layout import CentralWidget


class MainWindow(QMainWindow):
    appshutdown = Signal()
    send_logs = Signal(str, str, bool)

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.setWindowTitle("English Dictionary")
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

        app_icon = QIcon()
        app_icon.addFile(":/system_icons/tray_icon_16.png", QSize(16, 16))
        app_icon.addFile(":/system_icons/tray_icon_24.png", QSize(24, 24))
        app_icon.addFile(":/system_icons/tray_icon_48.png", QSize(48, 48))
        app_icon.addFile(":/system_icons/tray_icon_256.png", QSize(256, 256))
        self.app.setWindowIcon(app_icon)

        # Set system tray icon
        tray_icon = QSystemTrayIcon(app_icon, self.app)
        tray_menu = QMenu()
        maximize_action = QAction("Maximize", self)
        minimize_action = QAction("Minimize", self)
        quit_action = QAction("Quit", self)
        maximize_action.triggered.connect(self.showNormal)
        minimize_action.triggered.connect(self.showMinimized)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(maximize_action)
        tray_menu.addAction(minimize_action)
        tray_menu.addAction(quit_action)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.show()

        tray_icon.activated.connect(self.on_tray_icon_click)

    def on_tray_icon_click(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon click events. If minimized, show window as normal and bring to the font.
        If the window is already displayed, minimize the window.
        Args:
            reason (QSystemTrayIcon.ActivationReason): ActivationReason event when user clicks on the tray icon
        Returns:
            None: This function does not return a value.
        """
        if reason == QSystemTrayIcon.Trigger:
            # If the window is minimized, show it
            if self.isMinimized():
                self.showNormal()
                self.activateWindow()  # Bring the window to the front
            else:
                self.showMinimized()

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
