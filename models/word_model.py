from dataclasses import dataclass


@dataclass
class WordModel:
    guid: str
    word: str
    definition: str
    audio: str
    synonyms: str
    example: str
