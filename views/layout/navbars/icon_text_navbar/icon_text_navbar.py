from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from .icon_text_navbar_css import STYLES
from .icon_text_navbar_ui import IconTextNavBarView


class IconTextNavBar(QWidget):
    """
    Controller class for the expanded side navigation bar with icons and text buttons.

    Signals:
        btn_checked_ict (Signal[bool, QPushButton]): Emitted when a button is toggled.
        btn_clicked_page (Signal[QPushButton]): Emitted when a button is clicked.

    Attributes:
        ui (IconTextNavBarView): The view instance managing the UI components.
    """

    btn_checked_ict = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        """
        Initializes the IconTextNavBar controller. Sets up signal connections for button
        toggles and clicks, and initializes the UI layout.
        """
        super().__init__()

        self.setObjectName("icon_text_widget")
        self.setMaximumSize(QSize(250, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)

        self.ui = IconTextNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        self.ui.import_btn_ict.toggled.connect(self.btn_checked)
        self.ui.import_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.audio_btn_ict.toggled.connect(self.btn_checked)
        self.ui.audio_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.export_btn_ict.toggled.connect(self.btn_checked)
        self.ui.export_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.settings_btn_ict.toggled.connect(self.btn_checked)
        self.ui.settings_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.signout_btn_ict.toggled.connect(self.btn_checked)
        self.ui.signout_btn_ict.clicked.connect(self.btn_clicked)

        self.ui.import_btn_ict.setChecked(True)
        self.setHidden(True)

    def btn_checked(self, checked: bool) -> None:
        """
        Handles the button toggle state and emits the `btn_checked_ict` signal.

        Args:
            checked (bool): The checked state of the button.
        """
        self.btn_checked_ict.emit(checked, self.sender())

    def btn_clicked(self) -> None:
        """
        Handles the button click event and emits the `btn_clicked_page` signal.
        """
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool)
    def hide_nav(self, checked: bool) -> None:
        """
        Toggles the visibility of the navigation bar.

        Args:
            checked (bool): True if the navigation bar should be visible, False to hide.

        Returns:
            None: This function does not return a value.
        """
        self.setHidden(not checked)

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked: bool, btn: QPushButton) -> None:
        """
        Updates the checked state of the corresponding button based on the button object name.

        Args:
            checked (bool): The new checked state of the button.
            btn (QPushButton): The button that triggered the change.

        Returns:
            None: This function does not return a value.
        """
        match btn.objectName():
            case "import_btn_ico":
                self.ui.import_btn_ict.setChecked(checked)
            case "audio_btn_ico":
                self.ui.audio_btn_ict.setChecked(checked)
            case "export_btn_ico":
                self.ui.export_btn_ict.setChecked(checked)
            case "settings_btn_ico":
                self.ui.settings_btn_ict.setChecked(checked)
            case "signout_btn_ico":
                self.ui.signout_btn_ict.setChecked(checked)
