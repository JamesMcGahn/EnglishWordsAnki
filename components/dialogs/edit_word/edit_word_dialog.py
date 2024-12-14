from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from models import WordModel

from .edit_word_dialog_ui import EditWordDialogView


class EditWordDialog(QWidget):
    updated_word = Signal(WordModel)

    def __init__(self, word, title, label_text):
        super().__init__()
        self.word = word
        self.ui = EditWordDialogView()

        self.ui.setWindowTitle(title)
        self.ui.label.setText(label_text)
        self.ui.text_edit.setText(word.word)
        self.ui.submit_btn.clicked.connect(self.ok)
        self.ui.cancel_btn.clicked.connect(self.cancel)

    def exec(self):
        self.ui.exec()

    def ok(self):
        text = self.ui.text_edit.text()
        self.word.word = text
        self.updated_word.emit(self.word)
        self.ui.accept()

    def cancel(self):
        self.ui.reject()
