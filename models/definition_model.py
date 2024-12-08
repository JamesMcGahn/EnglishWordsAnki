from dataclasses import dataclass


@dataclass
class DefinitionModel:
    partOfSpeech: str
    definition: str
    synonyms: list
    antonyms: str
    example: str
