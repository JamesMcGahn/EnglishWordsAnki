from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QPushButton

from base import QWidgetBase

from .main_screen_ui import MainScreenView


class MainScreen(QWidgetBase):
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
    page_changed = Signal(int)
    send_app_settings = Signal()
    force_update = Signal()

    def __init__(self):
        """
        Initializes the MainScreen, sets up the UI, and connects signals for handling page changes and app shutdown.
        """
        super().__init__()
        self.ui = MainScreenView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.setObjectName("main_screen")

        self.ui.import_page.start_defining_words.connect(
            self.ui.define_page.start_define_words
        )
        self.ui.import_page.start_defining_words.connect(self.int_change_page)
        self.ui.define_page.start_audio_for_words.connect(self.int_change_page)
        self.ui.define_page.start_audio_for_words.connect(
            self.ui.audio_page.start_audio_words
        )
        self.ui.audio_page.start_sync_for_words.connect(self.int_change_page)
        self.ui.audio_page.start_sync_for_words.connect(
            self.ui.sync_page.start_sync_words
        )

        self.ui.settings_page.import_page_settings.connect(
            self.ui.import_page.receive_settings_update
        )
        self.ui.settings_page.audio_page_settings.connect(
            self.ui.audio_page.receive_settings_update
        )
        self.ui.settings_page.sync_page_settings.connect(
            self.ui.sync_page.receive_settings_update
        )

        self.ui.settings_page.log_page_settings.connect(
            self.ui.logs_page.receive_settings_update
        )

        self.appshutdown.connect(self.ui.import_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.define_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.audio_page.notified_app_shutting)
        self.appshutdown.connect(self.ui.sync_page.notified_app_shutting)
        self.send_app_settings.connect(self.ui.settings_page.send_all_settings)
        self.send_app_settings.emit()

    def int_change_page(self, index):
        print(index)
        self.ui.stackedWidget.setCurrentIndex(index)
        self.page_changed.emit(index)

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

        if btn_name.startswith("import_btn_"):
            self.ui.stackedWidget.setCurrentIndex(0)
        elif btn_name.startswith("define_btn_"):
            self.ui.stackedWidget.setCurrentIndex(1)
        elif btn_name.startswith("audio_btn_"):
            self.ui.stackedWidget.setCurrentIndex(2)
        elif btn_name.startswith("export_btn_"):
            self.ui.stackedWidget.setCurrentIndex(3)
        elif btn_name.startswith("logs_btn_"):
            self.ui.stackedWidget.setCurrentIndex(4)
        elif btn_name.startswith("settings_btn_"):
            self.ui.stackedWidget.setCurrentIndex(5)
        elif btn_name.startswith("signout_btn"):
            self.close_main_window.emit()
        self.force_update.emit()
