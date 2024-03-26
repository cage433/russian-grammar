import re
from functools import cached_property
from typing import List, Optional

from bs4 import BeautifulSoup

from grammar.conjugation import Conjugation, Aspect, IRREGULAR, RegularCategory, ZaliznyakClass, VerbType, \
    StressPattern, StressRule, Participle, ParticipleType, Tense, LongOrShort, PresentOrFutureConjugation, Imperative, \
    PastConjugation
from utils.types import checked_type


class ConjugationParser:
    CATEGORY_RE = re.compile(r' (\d{1,2})[abc] ')
    CATEGORY_RE_WITH_MODIFIER = re.compile(r' (\d{1,2})(.*)[abc]')
    STRESS_RE = re.compile(r'(?:-|\d)?([abc].*) ')
    STRESS2_RE = re.compile(r'(?:-|\d)?([abc].*)/([abc].*) ')

    def __init__(self, soup: BeautifulSoup):
        self.soup: BeautifulSoup = checked_type(soup, BeautifulSoup)

    @cached_property
    def conjugation_frame(self) -> BeautifulSoup:
        frames = self.soup.body.find_all("div", {"class": 'NavFrame'})
        return [f for f in frames if "Conjugation of" in f.text and "fective" in f.text][0]

    @cached_property
    def table_header(self):
        return self.conjugation_frame.find("div", {"class": 'NavHead'})

    @cached_property
    def extract_infinitive(self) -> str:
        return self.table_header.i.text

    @cached_property
    def extract_verb_type(self) -> VerbType:
        class_text = self.table_header.contents[-1].lower()
        is_intransitive = "intransitive" in class_text
        is_reflexive = "reflexive" in class_text
        if "irreg" in class_text:
            category = IRREGULAR
        elif match := self.CATEGORY_RE.search(class_text):
            category = RegularCategory(int(match.groups()[0]), modifier=None)
        elif match := self.CATEGORY_RE_WITH_MODIFIER.search(class_text):
            category = RegularCategory(int(match.groups()[0]), modifier=match.groups()[1])
        else:
            raise ValueError(f"Category not found in class text: {class_text}")

        if "imperfective" in class_text:
            aspect = Aspect.IMPERFECTIVE
        elif "perfective" in class_text:
            aspect = Aspect.PERFECTIVE
        else:
            raise ValueError(f"Aspect not found in class text: {class_text}")

        if stress_2 := self.STRESS2_RE.search(class_text):
            present_stress, past_stress = stress_2.groups()
            stress_rule = StressRule(
                StressPattern(present_stress), StressPattern(past_stress)
            )
        elif stress := self.STRESS_RE.search(class_text):
            stress = StressPattern(stress.groups()[0])
            stress_rule = StressRule(stress, past_stress=None)
        else:
            raise ValueError(f"Stress not found in class text: {class_text}")

        return VerbType(
            ZaliznyakClass(
                category=category,
                stress_rule=stress_rule
            ),
            aspect=aspect,
            transitive=not is_intransitive,
            reflexive=is_reflexive
        )

    def extract_participles_from_row(self, table_row: BeautifulSoup) -> List[Participle]:
        row_header = table_row.find('th').text.strip()
        participle_type = ParticipleType(row_header)
        present_cell, past_cell = table_row.find_all('td')

        def get_participles(texts: List[str], tense: Tense):
            # Sometimes obsolete participles are also shown
            texts = texts[:2]
            if len(texts) == 2:
                short, long = texts
                return [
                    Participle(short, participle_type, tense, LongOrShort.SHORT),
                    Participle(long, participle_type, tense, LongOrShort.LONG)
                ]
            elif len(texts) == 1:
                long = texts[0]
                return [Participle(long, participle_type, tense, LongOrShort.LONG)]
            else:
                assert len(texts) == 0, f"Unexpected number of participles: {texts}"
                return []

        present_participles = [a.text.strip() for a in present_cell.find_all('a')]
        past_participles = [a.text.strip() for a in past_cell.find_all('a')]
        participles = []
        participles += get_participles(present_participles, Tense.PRESENT)
        participles += get_participles(past_participles, Tense.PAST)
        return participles

    @cached_property
    def table(self):
        return self.conjugation_frame.find("div", {"class": 'NavContent'})

    @cached_property
    def table_rows(self):
        return self.table.find_all('tr')

    @cached_property
    def extract_participles(self) -> List[Participle]:
        rows = self.table_rows
        for i_row in [2, 6]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        participle_rows = rows[3:6]
        participles = []
        for row in participle_rows:
            participles += self.extract_participles_from_row(row)
        return participles

    def extract_present_or_future(self, aspect: Aspect) -> PresentOrFutureConjugation:
        rows = self.table_rows
        for i_row in [6, 13]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        p_or_f_rows = rows[7:13]
        texts = []
        for row in p_or_f_rows:
            cells = row.find_all('td')
            cell = cells[0] if aspect == Aspect.IMPERFECTIVE else cells[1]
            text = cell.find('a').text.strip()
            texts.append(text)

        return PresentOrFutureConjugation(
            first_person_singular=texts[0],
            second_person_singular=texts[1],
            third_person_singular=texts[2],
            first_person_plural=texts[3],
            second_person_plural=texts[4],
            third_person_plural=texts[5],
        )

    @cached_property
    def extract_imperative(self) -> Optional[Imperative]:
        rows = self.table_rows
        for i_row in [13, 15]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        imperative_row = rows[14]
        cells = imperative_row.find_all('td')
        texts = [
            a.text.strip()
            for c in cells
            for a in c.find_all('a')[:1]  # Sometimes there are multiple links
        ]
        if texts == []:
            return None
        singular, plural = texts
        return Imperative(singular, plural)

    @cached_property
    def extract_past_conjugation(self) -> PastConjugation:
        rows = self.table_rows
        singular_texts = []
        for row in rows[16:19]:
            text = row.find('td').find('a').text.strip()
            singular_texts.append(text)
        row_16_cells = rows[16].find_all('td')
        assert len(row_16_cells) == 2, f"Expected 2 cells in row 16, got {len(row_16_cells)}"
        plural_text = row_16_cells[1].find('a').text.strip()

        return PastConjugation(
            masculine=singular_texts[0],
            feminine=singular_texts[1],
            neuter=singular_texts[2],
            plural=plural_text
        )

    @cached_property
    def parse_conjugation_from_soup(self) -> Conjugation:
        infinitive = self.extract_infinitive
        verb_type = self.extract_verb_type
        participles = self.extract_participles
        present_or_future = self.extract_present_or_future(verb_type.aspect)
        imperative = self.extract_imperative
        past_conjugation = self.extract_past_conjugation
        return Conjugation(
            infinitive=infinitive,
            verb_type=verb_type,
            participles=participles,
            present_or_future=present_or_future,
            past=past_conjugation,
            imperative=imperative
        )
