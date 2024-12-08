from dataclasses import dataclass


@dataclass
class WordModel:
    word: str
    definition: str
    audio: str
    partOfSpeech: str
    synonyms: str
    example: str
