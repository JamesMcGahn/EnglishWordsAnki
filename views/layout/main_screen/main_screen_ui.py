from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy, QStackedWidget, QVBoxLayout, QWidget

from views.pages import DefinePage, ImportPage


class MainScreenView(QWidget):
    """
    MainScreenView is the view component for the main screen. It manages the UI layout
    and holds different pages like login, rules, settings, and logs using QStackedWidget.

    Attributes:
        main_screen_container_v (QVBoxLayout): The vertical layout that holds the stacked widget.
        stackedWidget (QStackedWidget): The stacked widget for switching between pages.
        rules_page (RulesPage): The page displaying rules.
        login_page (LoginPage): The page displaying the login form.
        settings_page (SettingsPage): The page displaying the settings.
        logs_page (LogsPage): The page displaying application logs.
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """init MainScreen View"""
        self.setObjectName("main_screen_ui")
        # Set size policy
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(16777215, 16777215))

        # Main layout container
        self.main_screen_container_v = QVBoxLayout(self)
        self.main_screen_container_v.setObjectName("main_screen_container_v")
        self.main_screen_container_v.setContentsMargins(1, 1, 1, 1)
        # Stacked widget to hold multiple pages
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("main_screen_stacked")
        # Pages
        self.import_page = ImportPage()
        self.define_page = DefinePage()
        self.settings_page = QWidget()
        self.logs_page = QWidget()
        # Add pages to stacked widget
        self.stackedWidget.addWidget(self.import_page)
        self.stackedWidget.addWidget(self.define_page)
        self.stackedWidget.addWidget(self.logs_page)
        self.stackedWidget.addWidget(self.settings_page)
        # Add the stacked widget to the main layout
        self.main_screen_container_v.addWidget(self.stackedWidget)
        self.stackedWidget.setCurrentIndex(0)
