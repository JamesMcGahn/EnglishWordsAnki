from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QWidget

from .multi_selection_dialog_ui import MultiSelectionDialogView


class MultiSelectionDialog(QWidget):
    md_multi_def_signal = Signal(list)

    def __init__(self, selections, title, label_text, exclusive=False):
        super().__init__()
        self.selections = selections
        self.ui = MultiSelectionDialogView()
        self.ui.select_btn_group.setExclusive(exclusive)
        self.ui.setWindowTitle(title)
        self.ui.label.setText(label_text)

        for i, selection in enumerate(self.selections):
            r = QCheckBox(f"{selection}")
            self.ui.select_btn_group.addButton(r, i)
            self.ui.in_dialog_layout.addWidget(r)
            r.clicked.connect(self.uncheck_none_btn)

        self.ui.select_btn_group.addButton(self.ui.none_btn, len(self.selections))

        self.ui.submit_btn.clicked.connect(self.ok)
        self.ui.cancel_btn.clicked.connect(self.cancel)

        self.ui.none_btn.clicked.connect(self.uncheck_on_none_btn_click)

    def uncheck_on_none_btn_click(self):
        for btn in self.ui.select_btn_group.buttons():
            if btn != self.ui.none_btn:
                btn.setChecked(False)

    def uncheck_none_btn(self):
        self.ui.none_btn.setChecked(False)

    def exec(self):
        self.ui.exec()

    def ok(self):

        selected_ids = []
        for button in self.ui.select_btn_group.buttons():
            if button.isChecked():

                button_id = self.ui.select_btn_group.id(button)
                selected_ids.append(button_id)
        if not selected_ids:
            selected_ids = [len(self.selections)]
        self.md_multi_def_signal.emit(selected_ids)
        self.ui.accept()

    def cancel(self):
        self.md_multi_def_signal.emit([len(self.selections)])
        self.ui.reject()
