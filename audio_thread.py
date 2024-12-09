from PySide6.QtCore import QThread, Signal

from google_audio_worker import GoogleAudioWorker


class AudioThread(QThread):
    finished = Signal()

    def __init__(self, words, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.words = words
        self.word_index = 0
        self.error_words = []
        self.success_words = []

    def run(self):
        self.download_next_word()

    def download_next_word(self):
        if self.word_index < len(self.words):
            self.worker = GoogleAudioWorker(
                self.words[self.word_index].word,
                f"{self.words[self.word_index].word}",
                self.folder_path,
            )
            self.worker.moveToThread(self)
            self.worker.success.connect(self.success_download)
            self.worker.error.connect(self.error_download)
            self.worker.do_work()

        else:
            self.finished.emit()
            print(self.success_words)
            print(self.error_words)

    def success_download(self):
        word = self.words[self.word_index]
        word.audio = f"[{self.words[self.word_index].word}.mp3]"
        self.success_words.append(word)
        self.word_index += 1
        self.download_next_word()

    def error_download(self):
        word = self.words[self.word_index]
        self.error_words.append(word)
        self.word_index += 1
        self.download_next_word()
