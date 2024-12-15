import subprocess
from time import sleep

from PySide6.QtCore import QObject, Signal, Slot


class SubprocessTasks(QObject):
    app_status = Signal(bool, str)
    app_opened = Signal(bool, str)
    app_checked_opened = Signal(bool, str)

    def __init__(self, app_name):
        super().__init__()
        self.app_name = app_name

    @Slot()
    def is_app_open(self):
        try:
            result = subprocess.check_output(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to (name of processes) contains "{self.app_name}"'
            ],
            text=True,
        )
            is_open = "true" in result.lower()
            message = f"{self.app_name} is {"open" if is_open else "closed"}"
            self.app_status.emit(is_open, message)
            return is_open
        except subprocess.CalledProcessError as e:
            message = f"When checking if {self.app_name} is open, an error occured: {e}"
            self.app_status.emit(False,message)
            return False
        except Exception as e:
            message = f"When checking if {self.app_name} is open, an error occured: {e}"
            self.app_status.emit(False,message)
            return False

    @Slot()
    def open_app(self):
        """Launches the application."""
        try:
            subprocess.run(["open", "-a", self.app_name])
            message = f"Opened Application - {self.app_name}"
            self.app_opened.emit(True, message)
        except subprocess.CalledProcessError as e:
            message = f"When opening {self.app_name} is open, an error occured: Make sure {self.app_name} is installed. \n Error: {e}"
            self.app_opened.emit(False, message)
        except Exception as e:
            message = f"When opening if {self.app_name} is open, an error occured: {e}"
            self.app_opened.emit(False, message)

    @Slot()
    def check_and_open(self):
        tries = 0
        app_open = self.is_app_open()

        while not app_open and tries < 2:
            self.open_app()
            sleep(3)  
            app_open = self.is_app_open()
            tries += 1

        if app_open:
            self.app_checked_opened.emit(True, f"{self.app_name} opened successfully!")
        else:
            self.app_checked_opened.emit(False, f"{self.app_name} failed to open!")