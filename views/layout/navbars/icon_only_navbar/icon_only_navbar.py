from PySide6.QtCore import QSize, Qt, Signal, Slot
from PySide6.QtWidgets import QPushButton, QWidget

from components.helpers import StyleHelper

from .icon_only_navbar_css import STYLES
from .icon_only_navbar_ui import IconOnlyNavBarView


class IconOnlyNavBar(QWidget):
    """
    Controller for the compressed side navigation bar with icon-only buttons.
    This class manages the behavior of the navigation buttons, including toggling
    and page changes.

    Signals:
        btn_checked_ico (Signal[bool, QPushButton]): Emitted when a button is toggled.
        btn_clicked_page (Signal[QPushButton]): Emitted when a button is clicked to change the page.

    Attributes:
        ui (IconOnlyNavBarView): The view component that defines the layout and widgets.
    """

    btn_checked_ico = Signal(bool, QPushButton)
    btn_clicked_page = Signal(QPushButton)

    def __init__(self):
        """
        Initializes the IconOnlyNavBar controller, connects signals to handle button interactions,
        and sets default states for the buttons.
        """
        super().__init__()
        self.setObjectName("icon_only_widget")
        self.setMaximumSize(QSize(70, 16777215))
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet(STYLES)
        # Set up the UI
        self.ui = IconOnlyNavBarView()
        self.layout = self.ui.layout()
        self.setLayout(self.layout)

        StyleHelper.drop_shadow(self)
        # Connect buttons to toggle and click events
        self.ui.import_btn_ico.toggled.connect(self.btn_checked)
        self.ui.import_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.define_btn_ico.toggled.connect(self.btn_checked)
        self.ui.define_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.audio_btn_ico.toggled.connect(self.btn_checked)
        self.ui.audio_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.export_btn_ico.toggled.connect(self.btn_checked)
        self.ui.export_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.settings_btn_ico.toggled.connect(self.btn_checked)
        self.ui.settings_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.signout_btn_ico.toggled.connect(self.btn_checked)
        self.ui.signout_btn_ico.clicked.connect(self.btn_clicked)

        self.ui.import_btn_ico.setChecked(True)

    @Slot(bool)
    def hide_nav(self, checked) -> None:
        """
        Slot to hide or show the navigation bar based on the checked state.

        Args:
            checked (bool): If True, the navigation bar will be hidden; if False, it will be shown.

        Returns:
            None: This function does not return a value.
        """
        self.setHidden(checked)

    def btn_checked(self, checked) -> None:
        """
        Slot that handles when a button is toggled, emitting a signal with the button's checked state.

        Args:
            checked (bool): The checked state of the button.

        Returns:
            None: This function does not return a value.
        """
        self.btn_checked_ico.emit(checked, self.sender())

    def btn_clicked(self) -> None:
        """
        Slot that handles when a button is clicked, emitting a signal to change the page.

        Returns:
            None: This function does not return a value.
        """
        self.btn_clicked_page.emit(self.sender())

    @Slot(bool, QPushButton)
    def btns_set_checked(self, checked, btn) -> None:
        """
        Slot that sets the checked state of a button based on its object name.

        Args:
            checked (bool): The checked state to set for the button.
            btn (QPushButton): The button to be checked.

        Returns:
            None: This function does not return a value.
        """
        match btn.objectName():
            case "import_btn_ict":
                self.ui.import_btn_ico.setChecked(checked)
            case "audio_btn_ict":
                self.ui.audio_btn_ico.setChecked(checked)
            case "define_btn_ict":
                self.ui.define_btn_ico.setChecked(checked)
            case "export_btn_ict":
                self.ui.export_btn_ico.setChecked(checked)
            case "settings_btn_ict":
                self.ui.settings_btn_ico.setChecked(checked)
            case "signout_btn_ict":
                self.ui.signout_btn_ico.setChecked(checked)
