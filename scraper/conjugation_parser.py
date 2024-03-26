import re
from typing import List

from bs4 import BeautifulSoup

from grammar.conjugation import Conjugation, Aspect, IRREGULAR, RegularCategory, ZaliznyakClass, VerbType, \
    StressPattern, StressRule, Participle, ParticipleType, Tense, LongOrShort, PresentOrFutureConjugation, Imperative, \
    PastConjugation


class ConjugationParser:
    CATEGORY_RE = re.compile(r' (\d{1,2})[abc]')
    STRESS_RE = re.compile(r'(?:-|\d)([abc]) ')
    STRESS2_RE = re.compile(r'(?:-|\d)([abc])/([abc])')

    @staticmethod
    def extract_infinitive(soup: BeautifulSoup) -> str:
        divs = soup.body.find("div", {"class": 'NavHead'})
        return divs.i.text

    @staticmethod
    def extract_verb_type(soup: BeautifulSoup) -> VerbType:
        divs = soup.body.find("div", {"class": 'NavHead'})
        class_text = divs.contents[-1].lower()
        is_intransitive = "intransitive" in class_text
        is_reflexive = "reflexive" in class_text
        if "irreg" in class_text:
            category = IRREGULAR
        else:
            match = ConjugationParser.CATEGORY_RE.search(class_text)
            if match is None:
                raise ValueError(f"Category not found in class text: {class_text}")
            category = RegularCategory(int(match.groups()[0]))

        if "imperfective" in class_text:
            aspect = Aspect.IMPERFECTIVE
        elif "perfective" in class_text:
            aspect = Aspect.PERFECTIVE
        else:
            raise ValueError(f"Aspect not found in class text: {class_text}")

        if stress_2 := ConjugationParser.STRESS2_RE.search(class_text):
            present_stress, past_stress = stress_2.groups()
            stress_rule = StressRule(
                StressPattern(present_stress), StressPattern(past_stress)
            )
        elif stress := ConjugationParser.STRESS_RE.search(class_text):
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

    @staticmethod
    def extract_participles_from_row(table_row: BeautifulSoup) -> List[Participle]:
        row_header = table_row.find('th').text.strip()
        participle_type = ParticipleType(row_header)
        present_cell, past_cell = table_row.find_all('td')

        def get_participles(texts: List[str], tense: Tense):
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

    @staticmethod
    def extract_participles(soup: BeautifulSoup) -> List[Participle]:
        table = soup.body.find("div", {"class": 'NavContent'})
        rows = table.find_all('tr')
        for i_row in [2, 6]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        participle_rows = rows[3:6]
        participles = []
        for row in participle_rows:
            participles += ConjugationParser.extract_participles_from_row(row)
        return participles

    @staticmethod
    def extract_present_or_future(soup: BeautifulSoup, aspect: Aspect) -> PresentOrFutureConjugation:
        table = soup.body.find("div", {"class": 'NavContent'})
        rows = table.find_all('tr')
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

    @staticmethod
    def extract_imperative(soup: BeautifulSoup) -> Imperative:
        table = soup.body.find("div", {"class": 'NavContent'})
        rows = table.find_all('tr')
        for i_row in [13, 15]:
            assert rows[i_row].attrs["class"] == ["rowgroup"], f" row {i_row} is not rowgroup"
        imperative_row = rows[14]
        texts = [
            a.text.strip() for a in imperative_row.find_all('a')
        ]
        singular, plural = texts
        return Imperative(singular, plural)

    @staticmethod
    def extract_past_conjugation(soup: BeautifulSoup) -> PastConjugation:
        table = soup.body.find("div", {"class": 'NavContent'})
        rows = table.find_all('tr')
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

    @staticmethod
    def parse_conjugation_from_soup(soup: BeautifulSoup) -> Conjugation:
        infinitive = ConjugationParser.extract_infinitive(soup)
        verb_type = ConjugationParser.extract_verb_type(soup)
        participles = ConjugationParser.extract_participles(soup)
        present_or_future = ConjugationParser.extract_present_or_future(soup, verb_type.aspect)
        imperative = ConjugationParser.extract_imperative(soup)
        past_conjugaton = ConjugationParser.extract_past_conjugation(soup)
        return Conjugation(
            infinitive=infinitive,
            verb_type=verb_type,
            participles=participles,
            present_or_future=present_or_future,
            past=past_conjugaton,
            imperative=imperative
        )
        return present_or_future
