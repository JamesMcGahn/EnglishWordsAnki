from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .main_screen_ui import MainScreenView


class MainScreen(QWidget):
    """
    MainScreen serves as the controller for the MainScreenView. It manages
    interactions between different parts of the view, such as changing pages and
    handling application shutdown.

    Attributes:
        ui (MainScreenView): The main screen view containing the stacked widget and its pages.
        layout (QLayout): The layout of the main screen.

    Signals:
        close_main_window (Signal): emits a notification to close the main window
    """

    close_main_window = Signal()

    def __init__(self):
        """
        Initializes the MainScreen, sets up the UI, and connects signals for handling page changes and app shutdown.
        """
        super().__init__()
        self.ui = MainScreenView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.setObjectName("main_screen")

    @Slot(QPushButton)
    def change_page(self, btn: QPushButton) -> None:
        """
        Changes the page displayed in the stacked widget based on the button clicked.

        Args:
            btn (QPushButton): The button that was clicked to trigger the page change.

        Returns:
            None: This function does not return a value.
        """
        btn_name = btn.objectName()

        if btn_name.startswith("keys_btn_"):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif btn_name.startswith("rules_btn_"):
            self.ui.stackedWidget.setCurrentIndex(1)
        elif btn_name.startswith("logs_btn_"):
            self.ui.stackedWidget.setCurrentIndex(2)
        elif btn_name.startswith("settings_btn_"):
            self.ui.stackedWidget.setCurrentIndex(3)
        elif btn_name.startswith("signout_btn"):
            self.close_main_window.emit()
