from pathlib import Path
from typing import List

from grammar.declinable import Declinable, SampleDeclinable
from utils.types import checked_type


class Noun(Declinable):

    def __init__(self, terms: List[List[str]]):
        super().__init__(terms)

    @property
    def type_names(self):
        return ["sing.", "pl."]

class SampleNoun(SampleDeclinable):
    def __init__(self, noun: Noun, text: str):
        super().__init__(noun, text)
        self.noun: Noun = checked_type(noun, Noun)

    @staticmethod
    def samples() -> List['SampleNoun']:
        path = Path(__file__).parent.parent / "resources" / "nouns"
        files = path.glob("*.txt")
        files = sorted(files)
        nouns = []
        for file in files:
            heading, terms = Declinable.parse_file(file)
            nouns.append(SampleNoun(Noun(terms), heading))
        return nouns

if __name__ == '__main__':
    foo = SampleNoun.samples()
    print(len(foo))