import sys

from PySide6.QtWidgets import QApplication

from views import MainWindow

app = QApplication(sys.argv)

window = MainWindow(app)
window.show()

app.exec()
