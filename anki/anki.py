from pathlib import Path
from typing import List, Optional

from grammar.conjugation import Conjugation, Aspect
from grammar.conjugation_data import find_conjugation
from grammar.constants import IRREGULAR_VERB_SET
from grammar.read_verbs import read_verbs_in_usage_order
from utils.utils import strip_stress_marks

CONJUGATIONS_DECK = "Conjugations"
IMPERFECT_DECK = "Imperfect"


def present_or_future_conjugation_note(conjugation: Conjugation):
    terms = [t for t in conjugation.present_or_future.terms]
    line = ""
    short_class = conjugation.verb_type.zaliznyak_class.short_class
    if len(short_class) == 1:
        short_class = "0" + short_class
    tag = "z-class:" + short_class
    if any([t is None for t in terms]):
        labels = [
            "1s", "2s", "3s", "1p", "2p", "3p"
        ]
        terms = [f"{l}: {t}" for l, t in zip(labels, terms) if t is not None]
    is_irregular = conjugation.verb_type.zaliznyak_class.is_irregular or strip_stress_marks(
        conjugation.infinitive) in IRREGULAR_VERB_SET
    if not is_irregular:
        terms = terms[:2]
    line += "<br>".join(terms) + "<br><br>"

    return ";".join([
        "Basic",
        CONJUGATIONS_DECK,
        tag,
        f"Conjugate {conjugation.infinitive};{line}"
    ])


def past_conjugation_note(conjugation: Conjugation):
    line = ""
    terms = [t for t in conjugation.past.terms]
    if any([t is None for t in terms]):
        labels = [
            "M", "F", "N", "P",
        ]
        terms = [f"{l}: {t}" for l, t in zip(labels, terms) if t is not None]
    if terms:
        line += "Past<br>"
        line += "<br>".join(terms) + "<br><br>"

    tag = "stress:" + conjugation.verb_type.zaliznyak_class.imperfect_stress_pattern
    return ";".join([
        "Basic",
        IMPERFECT_DECK,
        tag,
        f"Past tense of {conjugation.infinitive};{line}"
    ])


def write_anki_import_file(file_path: Path, notes: List[str]):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")
        f.write("#tags column:3\n")
        for n in notes:
            f.write(n + "\n")


def verb_conjugation_notes(c: Conjugation):
    return [
        present_or_future_conjugation_note(c),
        past_conjugation_note(c),
    ]


def create_common_conjugations():
    infinitives = [
        "быть", "сказать", "мочь", "говорить", "знать", "стать",
        "есть", "хотеть", "видеть", "идти", "стоять", "думать",
        "спросить", "жить", "смотреть", "сидеть", "понять", "иметь",
        "делать", "взять", "сделать", "понимать", "казаться", "давать",
        "пойти", "увидеть", "остаться", "выйти", "дать", "работать",
        "любить", "оказаться", "ответить", "подумать", "значить", "посмотреть",
        "ждать", "лежать", "найти", "писать", "решить", "вернуться",
        "считать", "помнить", "получить", "ходить", "бывать", "прийти",
        "узнать", "заметить",
    ]
    conjugations = [find_conjugation(i, force=False) for i in infinitives]
    notes = []
    for c in conjugations:
        notes += verb_conjugation_notes(c)
    write_anki_import_file(Path("/Users/alex/tmp/verbs.txt"), notes)


def create_all_verb_conjugations():
    verb_conjugations = read_verbs_in_usage_order(force=False)
    notes = []
    for c in verb_conjugations:
        notes += verb_conjugation_notes(c)
    write_anki_import_file(Path("/Users/alex/tmp/verbs.txt"), notes)


if __name__ == '__main__':
    create_all_verb_conjugations()
