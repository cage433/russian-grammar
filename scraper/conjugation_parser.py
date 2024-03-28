import re
from functools import cached_property
from typing import List, Optional

from bs4 import BeautifulSoup, Tag, NavigableString

from grammar.conjugation import Conjugation, Aspect, IRREGULAR, RegularCategory, ZaliznyakClass, VerbType, \
    StressPattern, StressRule, Participle, ParticipleType, Tense, LongOrShort, PresentOrFutureConjugation, Imperative, \
    PastConjugation, Participles
from utils.types import checked_type


class ConjugationParser:
    CATEGORY_RE = re.compile(r' (\d{1,2})[abc] ')
    CATEGORY_RE_WITH_MODIFIER = re.compile(r' (\d{1,2})(.*)[abc]')
    STRESS_RE = re.compile(r'(?:-|\d)?([abc].*) ')
    STRESS2_RE = re.compile(r'(?:-|\d)?([abc].*)/([abc].*) ')

    def __init__(self, soup: BeautifulSoup):
        self.soup: BeautifulSoup = checked_type(soup, BeautifulSoup)

    @cached_property
    def conjugation_frame(self) -> Optional[BeautifulSoup]:
        frames = self.soup.body.find_all("div", {"class": 'NavFrame'})
        matching_frames = [f for f in frames if "Conjugation of" in f.text and "fective" in f.text and "class" in f.text]
        if matching_frames == []:
            return None
        return matching_frames[0]

    @cached_property
    def table_header(self):
        return self.conjugation_frame.find("div", {"class": 'NavHead'})

    @cached_property
    def extract_infinitive(self) -> str:
        return self.table_header.i.text

    @cached_property
    def table_header_text(self):
        text = ""
        for t in self.table_header.contents:
            if isinstance(t, NavigableString):
                text += t
            if isinstance(t, Tag):
                text += t.text

        return text

    @cached_property
    def extract_verb_type(self) -> VerbType:
        class_text = self.table_header_text
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
    def extract_participles(self) -> Participles:
        rows = self.table_rows
        for i_row in [2, 6]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        participle_rows = rows[3:6]
        participles = []
        for row in participle_rows:
            participles += self.extract_participles_from_row(row)
        return Participles(participles)

    def extract_present_or_future(self, aspect: Aspect) -> PresentOrFutureConjugation:
        rows = self.table_rows
        for i_row in [6, 13]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        p_or_f_rows = rows[7:13]
        texts = []
        for row in p_or_f_rows:
            cells = row.find_all('td')
            cell = cells[0] if aspect == Aspect.IMPERFECTIVE else cells[1]
            links = cell.find_all('a')
            if len(links) == 0:
                text = None
            else:
                text = links[0].text.strip()
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
        def text_from_cell(cell):
            links = cell.find_all('a')
            if len(links) > 0:
                return links[0].text.strip()
            return cell.text.strip()

        singular = text_from_cell(cells[0])
        plural = text_from_cell(cells[1])
        # texts = [
        #     a.text.strip()
        #     for c in cells
        #     for a in c.find_all('a')[:1]  # Sometimes there are multiple links
        # ]
        # if texts == []:
        #     return None
        # singular, plural = texts
        return Imperative(singular, plural)

    @cached_property
    def extract_past_conjugation(self) -> PastConjugation:
        rows = self.table_rows
        singular_texts = []
        def get_text_from_cell(cell: Tag) -> Optional[str]:
            links = cell.find_all('a')
            if len(links) == 0:
                return None
            return links[0].text.strip()

        masculine = get_text_from_cell(rows[16].find('td'))
        feminine = get_text_from_cell(rows[17].find('td'))
        neuter = get_text_from_cell(rows[18].find('td'))
        plural = get_text_from_cell(rows[16].find_all('td')[1])

        return PastConjugation(
            masculine=masculine,
            feminine=feminine,
            neuter=neuter,
            plural=plural
        )

    def extract_other_aspect_infinitive(self, self_aspect) -> Optional[PresentOrFutureConjugation]:
        if self_aspect == Aspect.IMPERFECTIVE:
            other_aspect = self.soup.find_all('i', text='perfective')
        else:
            other_aspect = self.soup.find_all('i', text='imperfective')
        if len(other_aspect) >= 1:
            return other_aspect[0].text.strip()
        return None

    @cached_property
    def parse_conjugation_from_soup(self) -> Optional[Conjugation]:
        if self.conjugation_frame is None:
            return None
        infinitive = self.extract_infinitive
        verb_type = self.extract_verb_type
        other_aspect_infinitive = self.extract_other_aspect_infinitive(verb_type.aspect)
        participles = self.extract_participles
        present_or_future = self.extract_present_or_future(verb_type.aspect)
        imperative = self.extract_imperative
        past_conjugation = self.extract_past_conjugation
        return Conjugation(
            infinitive=infinitive,
            other_aspect=other_aspect_infinitive,
            verb_type=verb_type,
            participles=participles,
            present_or_future=present_or_future,
            past=past_conjugation,
            imperative=imperative
        )
