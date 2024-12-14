from collections import deque

from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from models import Status, WordModel
from utils.files.path_manager import PathManager

from .google_audio_worker import GoogleAudioWorker


class AudioThread(QThread):
    finished = Signal()

    audio_word = Signal(WordModel)
    error_word = Signal(WordModel)

    def __init__(self, words, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.words = deque(words)
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    def run(self):
        self.download_next_word()

    def download_next_word(self):
        self.pause_if_needed(self._stop)
        if  len(self.words) > 0:
            word = self.words.popleft()
            self.worker = GoogleAudioWorker(
                word.word,
                f"{word.word}",
                self.folder_path,
            )
            self.worker.moveToThread(self)
            self.worker.success.connect(lambda path: self.success_download(path,word))
            self.worker.error.connect(lambda: self.error_download(word))
            self.worker.do_work()

        else:
            self.finished.emit()

    @Slot(WordModel)
    def add_word_to_list(self, word):
        with QMutexLocker(self.mutex):
            self.words.append(word)

    def success_download(self, path, word):
        path_dict = PathManager.regex_path(path)
        word.audio_path = path
        word.audio = f"{path_dict["filename"]}{path_dict["ext"]}"
        word.status = Status.AUDIO
        self.audio_word.emit(word)
        self.download_next_word()

    def error_download(self, word):
        word.status = Status.SKIPPED_AUDIO
        self.error_word.emit(word)
        self.download_next_word()

    def pause_if_needed(self, checkVar):
        with QMutexLocker(self._mutex):
            if checkVar:
                self._paused = True

            while self._paused:
                self._wait_condition.wait(self._mutex)

    def resume(self):
        with QMutexLocker(self._mutex):  # Automatic lock and unlock
            self._paused = False
            self._wait_condition.wakeAll()