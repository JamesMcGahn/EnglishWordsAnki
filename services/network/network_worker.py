import requests
from PySide6.QtCore import QObject, Signal, Slot


class NetworkWorker(QObject):
    finished = Signal()
    response = Signal(object)
    error = Signal(str)

    def __init__(self, url, json):
        super().__init__()
        self.url = url
        self.json = json

    @Slot()
    def do_work(self):
        try:
            request = requests.get(self.url, json=self.json, timeout=10)
            res = request.json()
            self.response.emit(res)
        except requests.exceptions.ConnectionError as e:
            self.error.emit(e)
        except requests.exceptions.RequestException as e:
            self.error.emit(e)
        except Exception as e:

            self.error.emit(e)
        finally:
            self.finished.emit()
