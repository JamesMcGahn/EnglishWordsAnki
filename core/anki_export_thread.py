import subprocess
from collections import deque

import requests
from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from models import Status, WordModel


class AnkiExportThread(QThread):
    synced_word = Signal(WordModel)
    error_word = Signal(WordModel)
    dup_word = Signal(WordModel)
    finished = Signal()

    def __init__(self, words, deck_name, model_name):
        super().__init__()
        self.deck_name = deck_name
        self.model_name = model_name
        self.word_index = 0
        self.words = deque(words)
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    def run(self):
        print("started")
        self.open_notes_app()
        self.sync_next_word()

    def open_notes_app(self):
        """Launches the Anki application."""
        subprocess.run(["open", "-a", "Anki"])

    def sync_next_word(self):
        if len(self.words) > 0:
            word = self.words.popleft()
            try:
                payload = {
                    "action": "addNote",
                    "version": 6,
                    "params": {
                        "note": {
                            "deckName": f"{self.deck_name}",
                            "modelName": f"{self.model_name}",
                            "fields": {
                                "Word": f"{word.word}",
                                "Definition": f"{word.definition}",
                                "Audio": f"{word.audio}",
                                "Synonyms": f"{word.synonyms}",
                                "Example": f"{word.example}",
                            },
                            "options": {
                                "allowDuplicate": False,
                                "duplicateScope": "deck",
                                "duplicateScopeOptions": {
                                    "deckName": "English Words",
                                    "checkChildren": True,
                                    "checkAllModels": True,
                                },
                            },
                        }
                    },
                }

                response = requests.post(
                    "http://127.0.0.1:8765/", json=payload, timeout=20
                )

                response = response.json()

                if "error" in response:
                    if (
                        response["error"]
                        == "cannot create note because it is a duplicate"
                    ):
                        print("Word is a duplicate skipping")
                        word.status = Status.SKIPPED_ANKI_DUP
                        self.dup_word.emit(word)
                if response["result"] is not None:
                    id = response["result"]
                    print(f"Word is creating with id: {id}")
                    word.status = Status.ANKI_SYNCED
                    self.synced_word.emit(word)
            except requests.exceptions.ConnectTimeout as e:
                word.status = Status.SKIPPED_ANKI_ERROR
                self.error_word.emit(word)
            except Exception as e:
                word.status = Status.SKIPPED_ANKI_ERROR
                self.error_word.emit(word)
                print(e)
            finally:
                self.sync_next_word()
        else:
            self.cleanup()

    @Slot(WordModel)
    def add_word_to_list(self, word):
        with QMutexLocker(self.mutex):
            self.words.append(word)

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

    def cleanup(self):
        if not self.words:
            self.finished.emit()
        else:
            self.sync_next_word()
