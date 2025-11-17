import re
from functools import cached_property
from typing import List, Optional

from bs4 import BeautifulSoup, Tag, NavigableString

from grammar.conjugation import Conjugation, Aspect, ZaliznyakClass, VerbType, \
    Participle, ParticipleType, Tense, LongOrShort, PresentOrFutureConjugation, Imperative, \
    PastConjugation, Participles
from utils.types import checked_type


# Somewhat ugly code to parse the conjugation pages in Wiktionary
# Only needed once, as the results are stored in a shelf file
class ConjugationParser:
    zaliznyak_class_re = re.compile(r'class (.*) (?:im)?perfective')

    def __init__(self, conjugation_frame: Tag):
        self.conjugation_frame: Tag = checked_type(conjugation_frame, Tag)

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
        zaliznyak_class = self.zaliznyak_class_re.search(class_text).groups()[0]

        if "imperfective" in class_text:
            aspect = Aspect.IMPERFECTIVE
        elif "perfective" in class_text:
            aspect = Aspect.PERFECTIVE
        else:
            raise ValueError(f"Aspect not found in class text: {class_text}")

        return VerbType(
            ZaliznyakClass(
                zaliznyak_class
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
        return Imperative(singular, plural)

    @cached_property
    def extract_past_conjugation(self) -> PastConjugation:
        rows = self.table_rows

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

    @cached_property
    def parse_conjugation_from_soup(self) -> Optional[Conjugation]:
        if self.conjugation_frame is None:
            return None
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
