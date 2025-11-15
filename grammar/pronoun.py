from pathlib import Path
from typing import List

from grammar.declinable import Declinable, SampleDeclinable
from utils.types import checked_type

PRONOUNS_PATH = Path(__file__).parent.parent / "resources" / "pronouns"


class Pronoun(Declinable):
    def __init__(self, deck_name: str, terms: List[List[str]]):
        super().__init__(terms)
        self.deck_name = checked_type(deck_name, str)


class PersonalPronoun(Pronoun):
    def __init__(self, terms: List[List[str]]):
        super().__init__("Personal", terms)

    @property
    def type_names(self):
        return ["I", "you (s)", "he", "she", "it", "we", "you (pl)", "they"]


class AllGendersPronoun(Pronoun):
    def __init__(self, deck_name: str, terms: List[List[str]]):
        super().__init__(deck_name, terms)

    @property
    def type_names(self):
        return [""]


class GenderedPronoun(Pronoun):
    def __init__(self, deck_name: str, terms: List[List[str]]):
        super().__init__(deck_name, terms)

    @property
    def type_names(self):
        return ["m.", "f.", "n.", "pl."]


class SamplePronoun(SampleDeclinable):
    def __init__(self, pronoun: Pronoun, text: str):
        super().__init__(pronoun, text)
        self.pronoun: Pronoun = checked_type(pronoun, Pronoun)

    @staticmethod
    def samples() -> List['SamplePronoun']:
        samples = []

        def personal_pronoun(path):
            heading, terms = Declinable.parse_file(path)
            return SamplePronoun(PersonalPronoun(terms), heading)
        def gendered_pronoun(path, deck):
            heading, terms = Declinable.parse_file(path)
            return SamplePronoun(GenderedPronoun(deck, terms), heading)
        def all_genders_pronoun(path, deck):
            heading, terms = Declinable.parse_file(path)
            return SamplePronoun(AllGendersPronoun(deck, terms), heading)

        for path in (PRONOUNS_PATH / "interrogative").glob("*.txt"):
            samples.append(all_genders_pronoun(path, "Interrogative"))
        for path in (PRONOUNS_PATH / "demonstrative").glob("*.txt"):
            samples.append(gendered_pronoun(path, "Demonstrative"))
        for path in (PRONOUNS_PATH / "possessive").glob("*.txt"):
            samples.append(gendered_pronoun(path, "Possessive"))

        samples.append(
            gendered_pronoun(PRONOUNS_PATH / "reflexive" / "ones-own.txt", "Reflexive")
        )
        samples.append(
            all_genders_pronoun(PRONOUNS_PATH / "reflexive" / "self.txt", "Reflexive")
        )
        samples.append(gendered_pronoun(PRONOUNS_PATH / "all.txt", "Other"))
        samples.append(gendered_pronoun(PRONOUNS_PATH / "emphatic.txt", "Other"))
        samples.append(personal_pronoun(PRONOUNS_PATH / "personal.txt"))

        return samples


if __name__ == '__main__':
    for pronoun in SamplePronoun.samples():
        print(pronoun)
