from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Optional, List

from utils.types import checked_type, checked_list_type, checked_optional_type


class Aspect(StrEnum):
    PERFECTIVE = "perfective"
    IMPERFECTIVE = "imperfective"


class StressPattern:
    def __init__(self, pattern: str):
        self.pattern: str = checked_type(pattern, str)

    def __eq__(self, other):
        return self.pattern == other.pattern


def find_table_value(table: List[List[str]], key: str) -> Optional[str]:
    for row in table:
        if row[0] == key:
            return row[1]
    return None


class StressRule:
    PRESENT_STRESS = "present stress"
    PAST_STRESS = "past stress"

    def __init__(self, present_stress: StressPattern, past_stress: Optional[StressPattern]):
        self.present_stress: StressPattern = checked_type(present_stress, StressPattern)
        self.past_stress: Optional[StressPattern] = checked_optional_type(past_stress, StressPattern)

    def __str__(self):
        if self.past_stress is not None:
            return f"{self.present_stress}/{self.past_stress}"
        return f"{self.present_stress}"

    def to_table(self):
        table = [[self.PRESENT_STRESS, self.present_stress.pattern]]
        if self.past_stress is not None:
            table.append([self.PAST_STRESS, self.past_stress.pattern])
        return table

    @staticmethod
    def from_table(table: List[List[str]]):
        present_stress = find_table_value(table, StressRule.PRESENT_STRESS)
        past_stress = find_table_value(table, StressRule.PAST_STRESS)
        return StressRule(
            StressPattern(present_stress),
            StressPattern(past_stress) if past_stress is not None else None
        )

    def __eq__(self, other):
        return (
                self.present_stress == other.present_stress
                and self.past_stress == other.past_stress
        )


class Category(ABC):
    NUMBER = "Category Number"
    MODIFIER = "Category Modifier"
    IRREGULAR_LABEL = "Irregular"

    @abstractmethod
    def to_table(self) -> List[List[str]]:
        pass

    @staticmethod
    def from_table(table: List[List[str]]) -> 'Category':
        if find_table_value(table, Category.IRREGULAR_LABEL):
            return IRREGULAR

        number = int(find_table_value(table, Category.NUMBER))
        modifier = find_table_value(table, Category.MODIFIER)
        return RegularCategory(number, modifier)


class RegularCategory(Category):

    def __init__(self, number: int, modifier: Optional[str]):
        self.number: int = checked_type(number, int)
        self.modifier: Optional[str] = checked_optional_type(modifier, str)

    def __str__(self):
        if self.modifier is not None:
            return f"{self.number}{self.modifier}"
        return f"{self.number}"

    def to_table(self) -> List[List[str]]:
        table = [[Category.NUMBER, str(self.number)]]
        if self.modifier is not None:
            table.append([Category.MODIFIER, self.modifier])
        return table

    def __eq__(self, other):

        return (
            isinstance(other, RegularCategory)
                and self.number == other.number
                and self.modifier == other.modifier
        )


class IrregularCategory(Category):
    def __init__(self):
        pass

    def __str__(self):
        return "irregular"

    def to_table(self) -> List[List[str]]:
        return [[Category.IRREGULAR_LABEL, ""]]

    def __eq__(self, other):
        return isinstance(other, IrregularCategory)


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

    def to_table(self) -> List[List[str]]:
        category_table = self.category.to_table()
        stress_table = self.stress_rule.to_table()
        return category_table + stress_table

    @staticmethod
    def from_table(table: List[List[str]]) -> 'ZaliznyakClass':
        category = Category.from_table(table)
        stress_rule = StressRule.from_table(table)
        return ZaliznyakClass(category, stress_rule)

    def __eq__(self, other):
        return (
                self.category == other.category
                and self.stress_rule == other.stress_rule
        )


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
    PARTICIPLE_TEXT = "Participle Text"
    PARTICIPLE_TYPE = "Participle Type"
    PARTICIPLE_TENSE = "Participle Tense"
    PARTICIPLE_LONG_OR_SHORT = "Participle Long or Short"

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

    def to_table(self) -> List[List[str]]:
        return [
            [self.PARTICIPLE_TEXT, self.text],
            [self.PARTICIPLE_TYPE, self.participle_type],
            [self.PARTICIPLE_TENSE, self.tense],
            [self.PARTICIPLE_LONG_OR_SHORT, self.long_or_short]
        ]

    @staticmethod
    def from_table(table: List[List[str]]) -> 'Participle':
        text = find_table_value(table, Participle.PARTICIPLE_TEXT)
        participle_type = ParticipleType(find_table_value(table, Participle.PARTICIPLE_TYPE))
        tense = Tense(find_table_value(table, Participle.PARTICIPLE_TENSE))
        long_or_short = LongOrShort(find_table_value(table, Participle.PARTICIPLE_LONG_OR_SHORT))
        return Participle(text, participle_type, tense, long_or_short)

    def __eq__(self, other):
        return (
                self.text == other.text
                and self.participle_type == other.participle_type
                and self.tense == other.tense
                and self.long_or_short == other.long_or_short
        )


class Participles:
    def __init__(self, participles: List[Participle]):
        self.participles = checked_list_type(participles, Participle)

    def to_table(self) -> List[List[str]]:
        table = []
        for i, p in enumerate(self.participles):
            p_table = p.to_table()
            id_table = [[f"PART:{i}:{row[0]}", row[1]] for row in p_table]
            table += id_table
        return table

    @staticmethod
    def from_table(table: List[List[str]]) -> 'Participles':
        participle_table = [row for row in table if row[0].startswith("PART:")]
        sub_tables = {}
        for row in participle_table:
            _, i, key = row[0].split(":")
            row = [key, row[1]]
            if i not in sub_tables:
                sub_tables[i] = []
            sub_tables[i].append(row)
        participles = [
            Participle.from_table(value_table)
            for value_table in sub_tables.values()
        ]
        return Participles(participles)

    def __eq__(self, other):
        return self.participles == other.participles


class PresentOrFutureConjugation:
    POF_1S = "1st Sing"
    POF_2S = "2nd Sing"
    POF_3S = "3rd Sing"
    POF_1P = "1st Pl"
    POF_2P = "2nd Pl"
    POF_3P = "3rd Pl"
    TITLES = [POF_1S, POF_2S, POF_3S, POF_1P, POF_2P, POF_3P]

    def __init__(
            self,
            first_person_singular: Optional[str],
            second_person_singular: Optional[str],
            third_person_singular: Optional[str],
            first_person_plural: Optional[str],
            second_person_plural: Optional[str],
            third_person_plural: Optional[str],
    ):
        self.first_person_singular: Optional[str] = checked_optional_type(first_person_singular, str)
        self.second_person_singular: Optional[str] = checked_optional_type(second_person_singular, str)
        self.third_person_singular: Optional[str] = checked_optional_type(third_person_singular, str)
        self.first_person_plural: Optional[str] = checked_optional_type(first_person_plural, str)
        self.second_person_plural: Optional[str] = checked_optional_type(second_person_plural, str)
        self.third_person_plural: Optional[str] = checked_optional_type(third_person_plural, str)

        self.terms = [
            self.first_person_singular,
            self.second_person_singular,
            self.third_person_singular,
            self.first_person_plural,
            self.second_person_plural,
            self.third_person_plural
        ]

    def __str__(self):
        result = ""
        for title, term in zip(self.TITLES, self.terms):
            if term is not None:
                result += f"{title}: {term}\n"
        return result

    def to_table(self) -> List[List[str]]:
        table = []
        for title, term in zip(self.TITLES, self.terms):
            if term is not None:
                table.append([title, term])
        return table

    @staticmethod
    def from_table(table: List[List[str]]) -> 'PresentOrFutureConjugation':
        first_person_singular = find_table_value(table, PresentOrFutureConjugation.POF_1S)
        second_person_singular = find_table_value(table, PresentOrFutureConjugation.POF_2S)
        third_person_singular = find_table_value(table, PresentOrFutureConjugation.POF_3S)
        first_person_plural = find_table_value(table, PresentOrFutureConjugation.POF_1P)
        second_person_plural = find_table_value(table, PresentOrFutureConjugation.POF_2P)
        third_person_plural = find_table_value(table, PresentOrFutureConjugation.POF_3P)
        return PresentOrFutureConjugation(
            first_person_singular,
            second_person_singular,
            third_person_singular,
            first_person_plural,
            second_person_plural,
            third_person_plural
        )

    def __eq__(self, other):
        return (
                self.first_person_singular == other.first_person_singular
                and self.second_person_singular == other.second_person_singular
                and self.third_person_singular == other.third_person_singular
                and self.first_person_plural == other.first_person_plural
                and self.second_person_plural == other.second_person_plural
                and self.third_person_plural == other.third_person_plural
        )


class PastConjugation:
    PAST_M = "Past M"
    PAST_F = "Past F"
    PAST_N = "Past N"
    PAST_PL = "Past PL"

    def __init__(
            self,
            masculine: Optional[str],
            feminine: Optional[str],
            neuter: Optional[str],
            plural: Optional[str],
    ):
        self.masculine: Optional[str] = checked_optional_type(masculine, str)
        self.feminine: Optional[str] = checked_optional_type(feminine, str)
        self.neuter: Optional[str] = checked_optional_type(neuter, str)
        self.plural: Optional[str] = checked_optional_type(plural, str)

    def __str__(self):
        result = ""
        result += f"Masculine: {self.masculine}\n"
        result += f"Feminine: {self.feminine}\n"
        result += f"Neuter: {self.neuter}\n"
        result += f"Plural: {self.plural}\n"
        return result

    def to_table(self) -> List[List[str]]:
        return [
            [self.PAST_M, self.masculine],
            [self.PAST_F, self.feminine],
            [self.PAST_N, self.neuter],
            [self.PAST_PL, self.plural]
        ]

    @staticmethod
    def from_table(table: List[List[str]]) -> 'PastConjugation':
        masculine = find_table_value(table, PastConjugation.PAST_M)
        feminine = find_table_value(table, PastConjugation.PAST_F)
        neuter = find_table_value(table, PastConjugation.PAST_N)
        plural = find_table_value(table, PastConjugation.PAST_PL)
        return PastConjugation(masculine, feminine, neuter, plural)

    def __eq__(self, other):
        return (
                self.masculine == other.masculine
                and self.feminine == other.feminine
                and self.neuter == other.neuter
                and self.plural == other.plural
        )

class Imperative:
    IMP_S = "Imp S"
    IMP_PL = "Imp PL"

    def __init__(
            self,
            singular: str,
            plural: str,
    ):
        self.singular = singular
        self.plural = plural

    def __str__(self):
        return f"Singular: {self.singular}\nPlural: {self.plural}"

    def to_table(self) -> List[List[str]]:
        return [
            [self.IMP_S, self.singular],
            [self.IMP_PL, self.plural]
        ]

    @staticmethod
    def from_table(table: List[List[str]]) -> 'Optional[Imperative]':
        singular = find_table_value(table, Imperative.IMP_S)
        plural = find_table_value(table, Imperative.IMP_PL)
        if singular is None and plural is None:
            return None
        return Imperative(singular, plural)

    def __eq__(self, other):
        return (
                self.singular == other.singular
                and self.plural == other.plural
        )


class VerbType:
    ASPECT = "Aspect"
    TRANSITIVE = "Transitive"
    REFLEXIVE = "Reflexive"

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

    def to_table(self) -> List[List[str]]:
        return self.zaliznyak_class.to_table() + [
            [self.ASPECT, self.aspect],
            [self.TRANSITIVE, str(self.transitive)],
            [self.REFLEXIVE, str(self.reflexive)]
        ]

    @staticmethod
    def from_table(table: List[List[str]]) -> 'VerbType':
        zaliznyak_class = ZaliznyakClass.from_table(table)
        aspect = Aspect(find_table_value(table, VerbType.ASPECT))
        transitive = find_table_value(table, VerbType.TRANSITIVE) == "True"
        reflexive = find_table_value(table, VerbType.REFLEXIVE) == "True"
        return VerbType(zaliznyak_class, aspect, transitive, reflexive)

    def __eq__(self, other):
        return (
                self.zaliznyak_class == other.zaliznyak_class
                and self.aspect == other.aspect
                and self.transitive == other.transitive
                and self.reflexive == other.reflexive
        )


class Conjugation:
    def __init__(
            self,
            infinitive: str,
            other_aspect: Optional[str],
            verb_type: VerbType,
            participles: Participles,
            present_or_future: PresentOrFutureConjugation,
            past: PastConjugation,
            imperative: Optional[Imperative],
    ):
        self.infinitive: str = checked_type(infinitive, str)
        self.other_aspect: Optional[str] = checked_optional_type(other_aspect, str)
        self.verb_type: VerbType = checked_type(verb_type, VerbType)
        self.participles: Participles = checked_type(participles, Participles)
        self.present_or_future: PresentOrFutureConjugation = checked_type(present_or_future, PresentOrFutureConjugation)
        self.past: PastConjugation = checked_type(past, PastConjugation)
        self.imperative: Optional[Imperative] = checked_optional_type(imperative, Imperative)

    def __str__(self):
        result = ""
        result += f"Infinitive: {self.infinitive}\n"
        result += f"Type: {self.verb_type}\n"
        result += f"Participles:\n"
        for p in self.participles.participles:
            result += f"\t{p}\n"
        result += f"Present/Future:\n{self.present_or_future}\n"
        result += f"Past:\n{self.past}\n"
        if self.imperative is not None:
            result += f"Imperative:\n{self.imperative}\n"
        return result

    def to_table(self) -> List[List[str]]:
        table = [
            ["Infinitive", self.infinitive],
        ]
        if self.other_aspect is not None:
            table.append(["Other Aspect", self.other_aspect])
        table += self.verb_type.to_table()
        table += self.participles.to_table()
        table += self.present_or_future.to_table()
        table += self.past.to_table()
        if self.imperative is not None:
            table += self.imperative.to_table()
        return table

    @staticmethod
    def from_table(table: List[List[str]]) -> 'Conjugation':
        infinitive = find_table_value(table, "Infinitive")
        other_aspect = find_table_value(table, "Other Aspect")
        verb_type = VerbType.from_table(table)
        participles = Participles.from_table(table)
        present_or_future = PresentOrFutureConjugation.from_table(table)
        past = PastConjugation.from_table(table)
        imperative = Imperative.from_table(table)
        return Conjugation(infinitive, verb_type, participles, present_or_future, past, imperative)

    def __eq__(self, other):
        return (
                self.infinitive == other.infinitive
                and self.verb_type == other.verb_type
                and self.participles == other.participles
                and self.present_or_future == other.present_or_future
                and self.past == other.past
                and self.imperative == other.imperative
        )
