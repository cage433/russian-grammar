from abc import ABC
from enum import StrEnum
from typing import Optional, List

from utils.types import checked_type, checked_list_type, checked_optional_type


class Aspect(StrEnum):
    PERFECTIVE = "perfective"
    IMPERFECTIVE = "imperfective"


class StressPattern:
    def __init__(self, pattern: str):
        self.pattern: str = checked_type(pattern, str)


class StressRule:
    def __init__(self, present_stress: StressPattern, past_stress: Optional[StressPattern]):
        self.present_stress: StressPattern = checked_type(present_stress, StressPattern)
        self.past_stress: Optional[StressPattern] = checked_optional_type(past_stress, StressPattern)

    def __str__(self):
        if self.past_stress is not None:
            return f"{self.present_stress}/{self.past_stress}"
        return f"{self.present_stress}"


class Category(ABC):
    pass


class RegularCategory(Category):
    def __init__(self, number: int, modifier: Optional[str]):
        self.number: int = checked_type(number, int)
        self.modifier: Optional[str] = checked_optional_type(modifier, str)

    def __str__(self):
        return f"{self.number}"


class IrregularCategory(Category):
    def __init__(self):
        pass

    def __str__(self):
        return "irregular"


IRREGULAR = IrregularCategory()


class ZaliznyakClass:
    def __init__(
            self,
            category: Category,
            stress_rule: StressRule,
    ):
        self.category: Category = checked_type(category, Category)
        self.stress_rule: StressRule = checked_type(stress_rule, StressRule)

    def __str__(self):
        return f"{self.category}{self.stress_rule}"


class Tense(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


class Number(StrEnum):
    SINGULAR = "singular"
    PLURAL = "plural"


class ParticipleType(StrEnum):
    ACTIVE = "active"
    PASSIVE = "passive"
    ADVERBIAL = "adverbial"


class LongOrShort(StrEnum):
    LONG = "long"
    SHORT = "short"


class Participle:
    def __init__(
            self,
            text: str,
            participle_type: ParticipleType,
            tense: Tense,
            long_or_short: LongOrShort
    ):
        self.text: str = checked_type(text, str)
        self.participle_type: ParticipleType = checked_type(participle_type, ParticipleType)
        self.tense: Tense = checked_type(tense, Tense)
        self.long_or_short: LongOrShort = checked_type(long_or_short, LongOrShort)

    def __str__(self):
        return f"{self.text} ({self.participle_type}, {self.tense}, {self.long_or_short})"

    def __repr__(self):
        return str(self)


class PresentOrFutureConjugation:
    def __init__(
            self,
            first_person_singular: str,
            second_person_singular: str,
            third_person_singular: str,
            first_person_plural: str,
            second_person_plural: str,
            third_person_plural: str,
    ):
        self.first_person_singular: str = checked_type(first_person_singular, str)
        self.second_person_singular: str = checked_type(second_person_singular, str)
        self.third_person_singular: str = checked_type(third_person_singular, str)
        self.first_person_plural: str = checked_type(first_person_plural, str)
        self.second_person_plural: str = checked_type(second_person_plural, str)
        self.third_person_plural: str = checked_type(third_person_plural, str)

    def __str__(self):
        result = ""
        result += f"1st Sing: {self.first_person_singular}\n"
        result += f"2nd Sing: {self.second_person_singular}\n"
        result += f"3rd Sing: {self.third_person_singular}\n"
        result += f"2nd Pl: {self.first_person_plural}\n"
        result += f"2nd Pl: {self.second_person_plural}\n"
        result += f"3rd Pl: {self.third_person_plural}\n"
        return result


class PastConjugation:
    def __init__(
            self,
            masculine: str,
            feminine: str,
            neuter: str,
            plural: str,
    ):
        self.masculine: str = checked_type(masculine, str)
        self.feminine: str = checked_type(feminine, str)
        self.neuter: str = checked_type(neuter, str)
        self.plural: str = checked_type(plural, str)

    def __str__(self):
        result = ""
        result += f"Masculine: {self.masculine}\n"
        result += f"Feminine: {self.feminine}\n"
        result += f"Neuter: {self.neuter}\n"
        result += f"Plural: {self.plural}\n"
        return result


class Imperative:
    def __init__(
            self,
            singular: str,
            plural: str,
    ):
        self.singular = singular
        self.plural = plural

    def __str__(self):
        return f"Singular: {self.singular}\nPlural: {self.plural}"


class VerbType:
    def __init__(self,
                 zaliznyak_class: ZaliznyakClass,
                 aspect: Aspect,
                 transitive: bool,
                 reflexive: bool,
                 ):
        self.zaliznyak_class: ZaliznyakClass = checked_type(zaliznyak_class, ZaliznyakClass)
        self.aspect: Aspect = checked_type(aspect, Aspect)
        self.transitive: bool = checked_type(transitive, bool)
        self.reflexive: bool = checked_type(reflexive, bool)

    def __str__(self):
        tr = "transitive" if self.transitive else "intransitive"
        rf = "reflexive" if self.reflexive else "non-reflexive"
        return f"{self.zaliznyak_class} ({self.aspect}, {tr}, {rf})"


class Conjugation:
    def __init__(
            self,
            infinitive: str,
            verb_type: VerbType,
            participles: List[Participle],
            present_or_future: PresentOrFutureConjugation,
            past: PastConjugation,
            imperative: Optional[Imperative],
    ):
        self.infinitive: str = checked_type(infinitive, str)
        self.verb_type: VerbType = checked_type(verb_type, VerbType)
        self.participles: List[Participle] = checked_list_type(participles, Participle)
        self.present_or_future: PresentOrFutureConjugation = checked_type(present_or_future, PresentOrFutureConjugation)
        self.past: PastConjugation = checked_type(past, PastConjugation)
        self.imperative: Optional[Imperative] = checked_optional_type(imperative, Imperative)

    def __str__(self):
        result = ""
        result += f"Infinitive: {self.infinitive}\n"
        result += f"Type: {self.verb_type}\n"
        result += f"Participles:\n"
        for p in self.participles:
            result += f"\t{p}\n"
        result += f"Present/Future:\n{self.present_or_future}\n"
        result += f"Past:\n{self.past}\n"
        if self.imperative is not None:
            result += f"Imperative:\n{self.imperative}\n"
        return result
