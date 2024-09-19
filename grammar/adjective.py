from pathlib import Path
from typing import List

from grammar.declinable import Declinable, SampleDeclinable
from utils.types import checked_type


class Adjective(Declinable):

    def __init__(self, terms: List[List[str]]):
        super().__init__(terms)

    @property
    def type_names(self):
        return ["m.", "f.", "n.", "pl."]




class SampleAdjective(SampleDeclinable):
    def __init__(self, adjective: Adjective, text: str):
        super().__init__(adjective, text)
        self.adjective: Adjective = checked_type(adjective, Adjective)

    @staticmethod
    def samples() -> List['SampleAdjective']:
        path = Path(__file__).parent.parent / "resources" / "adjectives"
        files = path.glob("*.txt")
        files = sorted(files)
        adjectives = []
        for file in files:
            heading, terms = Declinable.parse_file(file)
            adjectives.append(SampleAdjective(Adjective(terms), heading))
        return adjectives

if __name__ == '__main__':
    foo = SampleAdjective.samples()
    print(len(foo))