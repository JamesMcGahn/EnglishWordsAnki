from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..gradient_dialog import GradientDialog
from .confirmation_dialog_css import STYLES


class ConfirmationDialog(GradientDialog):
    """
    A custom dialog for displaying a confirmation message with a gradient background.

    Args:
        title (str): The title of the dialog window.
        message (str): The message to display in the dialog.
        accept_btn_text (str, optional): button text for the accept button. Default's to Accept.
        parent (Optional[QWidget]): The parent widget of the dialog, defaults to None.
    """

    def __init__(
        self,
        title: str,
        message: str,
        accept_btn_text: str = "Accept",
        parent: Optional[QWidget] = None,
    ):
        gradient_colors = [(0.05, "#00A8E8"), (0.75, "#003366"), (1, "#003366")]
        super().__init__(gradient_colors, parent)
        self.title = title
        self.setFixedHeight(200)
        self.setFixedWidth(400)
        self.setWindowTitle(self.title)
        self.message = message

        self.setStyleSheet(STYLES)

        self.settings_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WA_StyledBackground, True)

        message_text_edit = QTextEdit(self.message)
        message_text_edit.setObjectName("error-text-edit")
        message_text_edit.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        message_text_edit.setReadOnly(True)

        self.settings_layout.addWidget(message_text_edit)

        self.close_btn = QPushButton(accept_btn_text)
        self.close_btn.setObjectName("close-btn")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel-btn")
        btn_box = QHBoxLayout()
        btn_box.setSpacing(8)
        btn_box.addWidget(self.cancel_btn)
        btn_box.addWidget(self.close_btn)

        self.settings_layout.addLayout(btn_box)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
