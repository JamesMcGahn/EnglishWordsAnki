from dataclasses import asdict
from typing import List

from PySide6.QtCore import QObject, Signal, Slot

from base import QSingleton
from services.settings import AppSettings

from .word_model import Status, WordModel


class WordsModel(QObject, metaclass=QSingleton):
    """
    Manages the words data for the application, allowing for adding,updated, deleting, saving, and resetting
    words. It interacts with persistent storage through AppSettings and emits signals when
    the data changes.

    Attributes:
        self._words (list): Internal list storing the words data.
        settings (AppSettings): The application settings instance for saving and loading rules.

    Signals:
        data_reset (list): Emitted when the model is reset.
        word_added (WordModel): Emits new word when a new word is added
        word_updated (WordModel): Emits updated word when a word is updated
        word_deleted (WordModel): Emits guid of deleted word when a word is deleted
    """

    data_reset = Signal(list)
    word_added = Signal(WordModel)
    word_updated = Signal(WordModel)
    word_deleted = Signal(str)
    word_added_to_be_defined = Signal(WordModel)
    word_added_to_be_audio = Signal(WordModel)
    word_added_to_be_sync = Signal(WordModel)
    word_added_synced = Signal(WordModel)

    def __init__(self):
        """
        Initializes the WordsModel with an empty list of rules and loads saved rules
        from persistent storage.
        """
        super().__init__()
        self._words = []
        self.settings = AppSettings()
        # #TODO reset enabled for test - remove line when done
        self.reset_model()
        self.init_words_model()

    @property
    def words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return self._words

    @property
    def undefined_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.ADDED]

    @property
    def to_be_defined_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.TO_BE_DEFINED]

    @property
    def skipped_defined_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.SKIPPED_DEFINED]

    @property
    def skipped_audio_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.SKIPPED_AUDIO]

    @property
    def skipped_sync_error(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [
            word for word in self._words if word.status == Status.SKIPPED_ANKI_ERROR
        ]

    @property
    def skipped_sync_duplicates(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.SKIPPED_ANKI_DUP]

    @property
    def to_be_audio_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.TO_BE_AUDIO]

    @property
    def to_be_synced_words(self) -> List:
        """
        Property to access the list of rule set.

        Returns:
            list: The list of current rule sets.
        """
        return [word for word in self._words if word.status == Status.TO_BE_SYNCED]

    @Slot(WordModel)
    def add_word(self, word: WordModel) -> None:
        """
        Adds a single rule to the model and emits the word_added signal.

        Args:
            rule (object): The rule to be added.

        Returns:
            None: This function does not return a value.
        """
        self._words.append(word)
        self.word_added.emit(word)

    @Slot(str)
    def delete_word(self, guid: str) -> None:
        """
        Delete the word from the words model. Emits word_deleted signal

        Args:
            guid (str): The guid of the word

        Returns:
            None: This function does not return a value.
        """
        if guid:
            words = [word for word in self.words if word.guid != guid]
            self._words = words
            self.word_deleted.emit(guid)

    @Slot(list)
    def delete_words(self, guids: list) -> None:
        """
        Delete the word from the words model. Emits word_deleted signal

        Args:
            guid (list): The guid of the word

        Returns:
            None: This function does not return a value.
        """
        words = []
        if guids:
            for word in self.words:
                if word.guid in guids:
                    continue
                else:
                    words.append(word)

            self._words = words

    @Slot()
    def delete_duplicates(self):
        words = [word for word in self.words if word.status != Status.SKIPPED_ANKI_DUP]
        self._words = words

    @Slot(str, WordModel)
    def update_word(self, guid: str, word: WordModel) -> None:
        """
        Update the word in the words model. Emits updated_word signal

        Args:
            guid (str): The guid of the rule set
            word (WordModel): The updated word

        Returns:
            None: This function does not return a value.
        """
        if guid:
            words = []

            for saved_word in self._words:
                if saved_word.guid != guid:
                    words.append(saved_word)
                elif saved_word.guid == guid:
                    words.append(word)
                    self.word_updated.emit(word)

            self._words = words

    @Slot()
    def reset_model(self) -> None:
        """
        Resets the model by clearing all words and updating the persistent storage.
        Emits the data_reset signal after the reset.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("word-model")
        self.settings.set_value("words-saved", [])
        self.settings.end_group()
        self._words = []
        self.data_reset.emit(self._words)

    @Slot()
    def save_words(self) -> None:
        """
        Saves the words to persistent storage.

        Returns:
            None: This function does not return a value.
        """
        self.settings.begin_group("word-model")
        self.settings.set_value("words-saved", [asdict(word) for word in self._words])
        self.settings.end_group()

    def init_words_model(self) -> None:
        """
        Initializes the word model by loading saved user words from persistent storage.
        If no words are found, an empty list is used for user words.
        """
        self.settings.begin_group("word-model")
        words = self.settings.get_value("words-saved", [])

        for word in words:

            saved_word = WordModel(**word)
            self._words.append(saved_word)
        self.settings.end_group()

    @Slot(str, Status)
    def update_status(self, guid, status):
        updated_status = []
        for word in self._words:
            if word.guid == guid:
                updated_word = word
                match status:
                    case Status.TO_BE_DEFINED:
                        updated_word.status = Status.TO_BE_DEFINED
                        self.word_added_to_be_defined.emit(word)
                    case Status.TO_BE_AUDIO:
                        updated_word.status = Status.TO_BE_AUDIO
                        self.word_added_to_be_audio.emit(word)
                    case Status.TO_BE_SYNCED:
                        updated_word.status = Status.TO_BE_SYNCED
                        self.word_added_to_be_sync.emit(word)
                    case Status.ANKI_SYNCED:
                        updated_word.status = Status.ANKI_SYNCED
                        self.word_added_synced.emit(word)
                updated_status.append(updated_word)
            else:
                updated_status.append(word)

        self._words = updated_status
