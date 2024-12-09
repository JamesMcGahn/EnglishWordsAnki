from dataclasses import dataclass


@dataclass
class WordModel:
    word: str
    definition: str
    audio: str
    synonyms: str
    example: str
