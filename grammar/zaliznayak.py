from abc import ABC, abstractmethod
from typing import Optional, List

from utils.types import checked_type, checked_optional_type


class StressPattern:
    def __init__(self, pattern: str):
        self.pattern: str = checked_type(pattern, str)

    def __eq__(self, other):
        return self.pattern == other.pattern


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

        number = find_table_value(table, Category.NUMBER)
        modifier = find_table_value(table, Category.MODIFIER)
        return RegularCategory(number, modifier)


class RegularCategory(Category):

    def __init__(self, number: str, modifier: Optional[str]):
        if number is None:
            print("here")
        self.number: int = checked_type(number, str)
        self.modifier: Optional[str] = checked_optional_type(modifier, str)

    def __str__(self):
        if self.modifier is not None:
            return f"{self.number}{self.modifier}"
        return f"{self.number}"

    def to_table(self) -> List[List[str]]:
        table = [[Category.NUMBER, self.number]]
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


