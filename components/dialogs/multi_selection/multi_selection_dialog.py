from PySide6.QtCore import Signal
from PySide6.QtWidgets import QRadioButton, QWidget

from .multi_selection_dialog_ui import MultiSelectionDialogView


class MultiSelectionDialog(QWidget):
    md_multi_def_signal = Signal(int)

    def __init__(self, selections):
        super().__init__()
        self.selections = selections
        self.ui = MultiSelectionDialogView()

        for i, selection in enumerate(self.selections):
            r = QRadioButton(f"{selection}")
            self.ui.select_btn_group.addButton(r, i)
            self.ui.in_dialog_layout.addWidget(r)

        self.ui.select_btn_group.addButton(self.ui.none_btn, len(self.selections))

        self.ui.submit_btn.clicked.connect(self.ok)
        self.ui.cancel_btn.clicked.connect(self.cancel)

    def exec(self):
        self.ui.exec()

    def ok(self):
        self.md_multi_def_signal.emit(self.ui.select_btn_group.checkedId())
        self.ui.accept()

    def cancel(self):
        self.md_multi_def_signal.emit(len(self.selections))
        self.ui.reject()
