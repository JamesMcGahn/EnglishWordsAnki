import requests
from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from models import DefinitionModel, Status, WordModel


class WordLookupWorker(QThread):
    send_logs = Signal(str, str, bool)
    result = Signal(list)
    finished = Signal()
    start_work = Signal()
    multi_definitions = Signal(str, list)
    multi_words = Signal(list)

    defined_word = Signal(WordModel)
    skipped_word = Signal(WordModel)

    def __init__(self, word_list):
        super().__init__()
        self.content = None
        self.word_list = word_list
        # self.start_work.connect(self.do_work)
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False
        self.multi_selection = None
        self.word_selection = None
        self.skipped_word_list = []
        self.words = []

    @Slot()
    def run(self):

        for list_word in self.word_list:
            self.pause_if_needed(self._stop)
            try:
                self.logging(f"Getting Definition for {list_word.word}")
                response = requests.get(
                    f"https://api.dictionaryapi.dev/api/v2/entries/en/{list_word.word}",
                    timeout=15,
                )
                res = response.json()

                # handle not finding word

                self.multi_selection = 0

                word_choices = []

                if "title" in res and res["title"] == "No Definitions Found":
                    self.logging(
                        f"No definitions found for word: {list_word.word} ...Skipping Word...",
                        "WARN",
                    )
                    list_word.status = Status.SKIPPED_DEFINED
                    self.skipped_word.emit(list_word)
                    continue

                self.logging(f"Found {len(res)} word for {list_word.word}")
                for word in res:
                    word_choice = {
                        "word": word["word"],
                        "partOfSpeech": word["meanings"][0]["partOfSpeech"],
                        "meaning": word["meanings"][0]["definitions"][0]["definition"],
                    }
                    word_choices.append(word_choice)

                with QMutexLocker(self._mutex):
                    if len(res) > 1:
                        self.logging("Pausing to ask User to Select Word Choice")
                        self.multi_words.emit(word_choices)
                        self._paused = True

                    while self._paused:
                        self._wait_condition.wait(self._mutex)

                if self.word_selection == len(word_choices):
                    self.logging("User did not select a word choice. Skipping word...")
                    list_word.status = Status.SKIPPED_DEFINED
                    self.skipped_word.emit(list_word)
                    continue

                if len(res) > 1:
                    self.logging(f"User selected option {self.word_selection + 1}")
                    word = res[self.word_selection]
                else:
                    word = res[0]

                meanings = word["meanings"]
                self.logging(
                    f"Found {len(meanings)} meanings for word: {list_word.word}"
                )
                all_meanings = []
                for meaning in meanings:
                    for definition in meaning["definitions"]:
                        a_meaning = DefinitionModel(
                            meaning["partOfSpeech"],
                            definition.get("definition", ""),
                            definition.get("synonyms") or meaning.get("synonyms", []),
                            definition.get("antonyms") or meaning.get("antonyms", []),
                            definition.get("example", ""),
                        )
                        all_meanings.append(a_meaning)

                with QMutexLocker(self._mutex):
                    if len(all_meanings) > 1:
                        self.logging("Asking User for meanings they want to keep.")
                        self.multi_definitions.emit(list_word.word, all_meanings)
                        self._paused = True

                    while self._paused:
                        self._wait_condition.wait(self._mutex)

                if len(all_meanings) > 1 and self.multi_selection[0] == len(
                    all_meanings
                ):
                    list_word.status = Status.SKIPPED_DEFINED
                    self.logging(
                        "User did not select a word meanings. Skipping word..."
                    )
                    self.skipped_word.emit(list_word)
                    continue

                def add_non_duplicates(original_list, new_items):
                    return list(set(original_list).union(new_items))

                if len(all_meanings) == 1:
                    self.multi_selection = [0]
                all_meanings = [all_meanings[i] for i in self.multi_selection]
                word_name = word["word"]
                definition_string = ""
                synonyms = ""
                example = ""
                audio = ""

                for meaning in all_meanings:
                    print(meaning)
                    definition_string += (
                        f"{meaning.partOfSpeech} - {meaning.definition}"
                    )
                    synonyms = add_non_duplicates(synonyms, meaning.synonyms)
                    example += meaning.example

                list_word.status = Status.DEFINDED
                list_word.word = word_name
                list_word.definition = definition_string
                list_word.audio = audio
                list_word.synonyms = ", ".join(meaning.synonyms)
                list_word.example = example
                self.logging(f"Completed word: {list_word.word}")
                self.defined_word.emit(list_word)

            except Exception as e:
                print(e)
        self.logging("No more words left. Ending word look up.")
        self.finished.emit()

    @Slot(WordModel)
    def add_word_to_list(self, word):
        with QMutexLocker(self._mutex):
            self.word_list.append(word)

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

    @Slot(list)
    def get_user_definition_selection(self, choices):
        self.multi_selection = choices
        self.resume()

    @Slot(int)
    def get_user_word_selection(self, choice):
        self.word_selection = choice
        self.resume()

    @Slot(str, str, bool)
    def logging(self, msg: str, level: str = "INFO", print_msg: bool = True) -> None:
        """
        Logs a message with the specified log level.

        This method send logs to Logger with a message, log level, and
        an optional flag to print the message.

        Args:
            msg (str): The message to be logged.
            level (str, optional): The log level (e.g., "INFO", "WARN", "ERROR"). Defaults to "INFO".
            print_msg (bool, optional): Flag to determine whether to print the log message. Defaults to True.

        Returns:
            None
        """
        self.send_logs.emit(msg, level, print_msg)
