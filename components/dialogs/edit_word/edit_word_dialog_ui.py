from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)


class EditWordDialogView(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        self.dialog_layout = QVBoxLayout()
        self.label = QLabel()
        self.dialog_layout.addWidget(self.label)
        self.text_edit = QLineEdit()

        self.in_dialog_layout = QVBoxLayout()
        self.none_btn = QCheckBox("None of these")
        self.in_dialog_layout.addWidget(self.text_edit)
        self.dialog_layout.addLayout(self.in_dialog_layout)
        self.dialog_md_hlayout = QHBoxLayout()
        self.dialog_md_hlayout.setObjectName("dialog_md_hlayout")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum
        )
        self.dialog_md_hlayout.addItem(self.horizontalSpacer)

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submit_button")

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_button")

        self.dialog_md_hlayout.addWidget(self.cancel_btn)
        self.dialog_md_hlayout.addWidget(self.submit_btn)

        self.dialog_layout.addLayout(self.dialog_md_hlayout)
        self.setLayout(self.dialog_layout)
