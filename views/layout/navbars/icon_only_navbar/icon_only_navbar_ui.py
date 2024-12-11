from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from components.helpers import WidgetFactory


class IconOnlyNavBarView(QWidget):
    """
    A compressed side navigation bar with icon-only buttons. This navigation bar includes buttons for keys, rules, logs,
    settings, and sign-out, each with corresponding icons that change on hover or click.

    Attributes:
        icon_nav_vlayout (QVBoxLayout): The main vertical layout for the navigation bar.
        icon_btn_layout (QVBoxLayout): The layout that holds the icon-only buttons.
        import_btn_ico (QPushButton): Button for the 'Keys' section.
        audio_btn_ict (QPushButton): Button for the 'Rules' section.
        export_btn_ico (QPushButton): Button for the 'Logs' section.
        settings_btn_ico (QPushButton): Button for the 'Settings' section.
        signout_btn_ico (QPushButton): Button for the 'Sign Out' action.
        verticalSpacer_2 (QSpacerItem): A spacer item to separate buttons from the bottom.
    """

    def __init__(self):
        """
        Initializes the IconOnlyNavBarView and sets up the UI.
        """
        super().__init__()
        self.init_ui()
        self.setObjectName("icon_only_widget_ui")

    def init_ui(self) -> None:
        """
        Initializes the UI components, including buttons and icons, for the side navigation bar.

        Returns:
            None: This function does not return a value.
        """
        self.setMaximumSize(QSize(70, 16777215))
        self.setMinimumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)
        # Main layout for the icon navigation bar
        self.icon_nav_vlayout = QVBoxLayout(self)
        self.icon_nav_vlayout.setObjectName("icon_nav_vlayout")
        # Layout for the icon buttons
        self.icon_btn_layout = QVBoxLayout()
        self.icon_btn_layout.setObjectName("icon_btn_layout_ico")
        # Create buttons for the navigation items
        self.import_btn_ico = QPushButton()
        self.import_btn_ico.setObjectName("import_btn_ico")
        self.icon_btn_layout.addWidget(self.import_btn_ico)

        self.audio_btn_ico = QPushButton()
        self.audio_btn_ico.setObjectName("audio_btn_ico")
        self.icon_btn_layout.addWidget(self.audio_btn_ico)

        self.export_btn_ico = QPushButton()
        self.export_btn_ico.setObjectName("export_btn_ico")
        self.icon_btn_layout.addWidget(self.export_btn_ico)

        self.settings_btn_ico = QPushButton()
        self.settings_btn_ico.setObjectName("settings_btn_ico")

        self.signout_btn_ico = QPushButton()
        self.signout_btn_ico.setObjectName("signout_btn_ico")

        icons = [
            (
                self.import_btn_ico,
                ":/images/import_on.png",
                ":/images/import_black.png",
            ),
            (
                self.audio_btn_ico,
                ":/images/audio_on.png",
                ":/images/audio_black.png",
            ),
            (
                self.export_btn_ico,
                ":/images/export_on.png",
                ":/images/export_black.png",
            ),
            (
                self.settings_btn_ico,
                ":/images/settings_on.png",
                ":/images/settings_black.png",
            ),
            (
                self.signout_btn_ico,
                ":/images/signout_on.png",
                ":/images/signout_black.png",
            ),
        ]
        # Create icons for each button
        for icon in icons:
            parent, image_loc_1, image_loc_2 = icon
            WidgetFactory.create_icon(
                parent, image_loc_1, 100, 20, True, image_loc_2, True
            )

        self.icon_nav_vlayout.addLayout(self.icon_btn_layout)
        # Spacer to push the settings and signout buttons to the bottom
        self.verticalSpacer_2 = QSpacerItem(
            43, 589, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.icon_nav_vlayout.addItem(self.verticalSpacer_2)
        # Add settings and sign-out buttons at the bottom
        self.icon_nav_vlayout.addWidget(self.settings_btn_ico)
        self.icon_nav_vlayout.addWidget(self.signout_btn_ico)
