from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.helpers import StyleHelper, WidgetFactory


class HeaderNavBarView(QWidget):
    """
    HeaderNavBarView is the view component for the header navigation bar.
    It includes an application logo, a file open button, and a hamburger menu button.

    Attributes:
        navbar_vlayout (QVBoxLayout): The vertical layout that holds the header elements.
        inner_cont_hlayout (QHBoxLayout): The layout holding the logo, spacer, and buttons.
        app_logo_vlayout (QVBoxLayout): Layout specifically for the application logo.
        app_logo (QLabel): The label displaying the application logo.
        open_file_btn (GradientButton): Button for opening a file.
        hamburger_icon_btn (QPushButton): Button for toggling the navigation menu.
        horizontalSpacer_3 (QSpacerItem): A spacer between the logo and buttons.
    """

    def __init__(self):
        """
        Initializes the HeaderNavBarView and sets up the UI layout.
        """
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI elements of the header navigation bar, setting up the layout and widgets.

        Returns:
            None: This function does not return a value.
        """
        self.setObjectName("header_widget_ui")
        # Main vertical layout
        self.navbar_vlayout = QVBoxLayout(self)
        self.navbar_vlayout.setObjectName("navbar_vlayout")
        # Inner horizontal layout for logo and buttons
        self.inner_cont_hlayout = QHBoxLayout()
        self.inner_cont_hlayout.setObjectName("inner_cont_hlayout")
        # Layout for application logo
        self.app_logo_vlayout = QVBoxLayout()
        self.app_logo_vlayout.setObjectName("app_logo_vlayout")
        # Application logo
        self.app_logo = QLabel(self)
        self.app_logo.setObjectName("app_logo")
        self.app_logo.setStyleSheet("text-align: right;")
        original_pixmap = QPixmap(":/images/logo.png")
        self.app_logo.setPixmap(original_pixmap)
        StyleHelper.drop_shadow(self.app_logo)
        self.app_logo_vlayout.addWidget(self.app_logo)
        # Spacer between logo and buttons
        self.horizontalSpacer_3 = QSpacerItem(
            558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        # Add logo layout and spacer to the inner horizontal layout
        self.inner_cont_hlayout.addLayout(self.app_logo_vlayout)
        self.inner_cont_hlayout.addItem(self.horizontalSpacer_3)
        # Open file button

        # Hamburger menu button
        self.hamburger_icon_btn = QPushButton(self)
        StyleHelper.drop_shadow(self.hamburger_icon_btn)
        self.hamburger_icon_btn.setObjectName("hamburger-icon-btn")
        self.hamburger_icon_btn.setStyleSheet(
            "QPushButton {\n" "border: none;\n" "padding-right:.5em\n" "}"
        )
        # Create the hamburger icon
        WidgetFactory.create_icon(
            self.hamburger_icon_btn,
            ":/images/hamburger_off.png",
            29,
            35,
            True,
            ":/images/hamburger_on.png",
            False,
        )
        # Add hamburger button to the horizontal layout
        self.inner_cont_hlayout.addWidget(self.hamburger_icon_btn)
        # Add inner horizontal layout to the main vertical layout
        self.navbar_vlayout.addLayout(self.inner_cont_hlayout)
