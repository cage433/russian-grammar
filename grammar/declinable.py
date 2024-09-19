from abc import abstractmethod
from pathlib import Path
from typing import List, Tuple

from utils.types import checked_type


class Declinable:
    NOM, ACC, GEN, DAT, INST, PREP = range(6)

    def __init__(self, terms: List[List[str]]):
        self.terms: List[List[str]] = terms

    def declension(self, i_type):
        return [t[i_type] for t in self.terms]

    @property
    @abstractmethod
    def type_names(self):
        raise ValueError("Must be implemented in subclass")

    @property
    def root(self):
        return self.terms[0][0]

    @property
    def nominative(self):
        return self.terms[self.NOM]

    @property
    def accusative(self):
        return self.terms[self.ACC]

    @property
    def genitive(self):
        return self.terms[self.GEN]

    @property
    def dative(self):
        return self.terms[self.DAT]

    @property
    def instrumental(self):
        return self.terms[self.INST]

    @property
    def prepositional(self):
        return self.terms[self.PREP]

    @staticmethod
    def parse_file(file: Path) -> Tuple[str, List[List[str]]]:
        with open(file) as f:
            lines = f.readlines()
            heading = lines[0].strip()
            declension_lines = lines[1:7]
            terms = []
            for line in declension_lines:
                case_terms = [t.strip() for t in line.split(",")]
                terms.append(case_terms)
            return (heading, terms)

class SampleDeclinable:
    def __init__(self, declinable: Declinable, text: str):
        self.declinable: Declinable = checked_type(declinable, Declinable)
        self.text: str = checked_type(text, str)
