from dataclasses import dataclass
from enum import Enum, auto


class Status(Enum):
    ADDED = auto()
    TO_BE_DEFINED = auto()
    DEFINDED = auto()
    TO_BE_AUDIO = auto()
    AUDIO = auto()
    TO_BE_SYNCED = auto()
    ANKI_SYNCED = auto()
    SKIPPED_AUDIO = auto()
    SKIPPED_DEFINED = auto()
    SKIPPED_ANKI_DUP = auto()
    SKIPPED_ANKI_ERROR = auto()


@dataclass
class WordModel:
    status: Status
    guid: str
    word: str
    definition: str
    audio: str
    audio_path: str
    synonyms: str
    example: str
