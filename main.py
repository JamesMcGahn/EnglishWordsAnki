# import faulthandler
import sys

from PySide6.QtWidgets import QApplication

from views import MainWindow

# faulthandler.enable(file=sys.stderr)
# faulthandler.enable()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()
