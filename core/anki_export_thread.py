import requests
from PySide6.QtCore import QThread, Signal


class AnkiExportThread(QThread):

    def __init__(self, words, deck_name, model_name):
        super().__init__()
        self.words = words
        self.deck_name = deck_name
        self.model_name = model_name
        self.word_index = 0

    def run(self):
        print("started")
        for word in self.words:
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
                if response["result"] is not None:
                    id = response["result"]
                    print(f"Word is creating with id: {id}")
            except requests.exceptions.RequestTimeout as e:
                pass
            except Exception as e:
                print(e)
