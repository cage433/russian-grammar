from pathlib import Path
from typing import List

from grammar.adjective import SampleAdjective
from grammar.conjugation import Conjugation
from grammar.conjugation_data import find_conjugation
from grammar.declinable import Declinable, SampleDeclinable
from grammar.noun import SampleNoun
from grammar.read_verbs import read_verbs_in_usage_order
from grammar.read_vocab import read_vocab_10000, Vocab
from utils.utils import strip_stress_marks

CONJUGATIONS_DECK = "Conjugations"
IMPERFECT_DECK = "Imperfect"
RUSSIAN_TO_ENGLISH_DECK = "Vocab::Russian to English"
ENGLISH_TO_RUSSIAN_DECK = "Vocab::English to Russian"
VOCAB_10000_DECK = "Vocab::10000 words"
ADJECTIVE_DECK = "Adjectives"
NOUN_DECK = "Nouns"


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
    to_conjugate_fully = {"быть", "есть", "дать", "бежать", "хотеть", "мочь"}
    if not strip_stress_marks(conjugation.infinitive) in to_conjugate_fully:
        terms = terms[:2] + terms[-1:]
    line += "<br>".join(terms) + "<br><br>"

    return ";".join([
        "Basic",
        CONJUGATIONS_DECK,
        tag,
        f"Conjugate {conjugation.infinitive};{line}"
    ])


def past_conjugation_note(conjugation: Conjugation) -> str:
    line = ""
    terms = [t for t in conjugation.past.terms]
    if any([t is None for t in terms]):
        labels = [
            "M", "F", "N", "P",
        ]
        terms = [f"{l}: {t}" for l, t in zip(labels, terms) if t is not None]
    if terms:
        line += "<br>".join(terms) + "<br><br>"

    tag = "stress:" + conjugation.verb_type.zaliznyak_class.imperfect_stress_pattern
    return ";".join([
        "Basic",
        IMPERFECT_DECK,
        tag,
        f"Past tense of {conjugation.infinitive};{line}"
    ])



def russian_to_english_notes(vocab: Vocab) -> List[str]:
    return [
        ";".join([
            "Basic",
            RUSSIAN_TO_ENGLISH_DECK,
            f"{item.russian}<br><br>;{item.english}<br><br>{item.notes}"
        ])
        for item in vocab.items
    ]


def english_to_russian_notes(vocab: Vocab):
    return [
        ";".join([
            "Basic",
            ENGLISH_TO_RUSSIAN_DECK,
            f"{item.english};{item.russian}<br><br>{item.notes}<br><br>"
        ])
        for item in vocab.items
    ]

def vocab_10000_notes(vocab: Vocab):
    return [
        ";".join([
            "Basic (and reversed card)",
            VOCAB_10000_DECK,
            f"{item.english};{item.russian}<br><br>"
        ])
        for item in vocab.items
    ]


def _case_notes(deck: str, sample: SampleDeclinable):
    decl = sample.declinable
    def case_note(case: str, declension: List[str]):
        question = f"{decl.root} {case} ({sample.text})"
        answer = "<br>".join(declension)
        return ";".join([
            "Basic",
            deck,
            f"{question};{answer}<br><br>"
        ])
    return [
        case_note("nom.", decl.nominative),
        case_note("acc.", decl.accusative),
        case_note("gen.", decl.genitive),
        case_note("dat.", decl.dative),
        case_note("inst.", decl.instrumental),
        case_note("prep.", decl.prepositional),
    ]

def _declension_notes(deck: str, sample: SampleDeclinable):
    decl = sample.declinable
    type_names = decl.type_names
    def _declension_note(i_type: int):
        question = f"{decl.root} {type_names[i_type]} ({sample.text})"
        answer = "<br>".join(decl.declension(i_type))
        return ";".join([
            "Basic",
            deck,
            f"{question};{answer}<br><br>"
        ])
    return [
        _declension_note(i_type)
        for i_type in range(len(type_names))
    ]

def declinable_notes(deck: str, sample: SampleDeclinable):
    return _declension_notes(deck, sample) + _case_notes(deck, sample)

def adjective_notes(sample: SampleAdjective):
    return declinable_notes(ADJECTIVE_DECK, sample)

def noun_notes(sample: SampleNoun):
    return declinable_notes(NOUN_DECK, sample)

def write_anki_import_file(file_path: Path, notes: List[str], include_tag_column: bool):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")
        if include_tag_column:
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


def create_vocab_10000_one_sided_decks(force: bool):
    vocab = read_vocab_10000(force=force)
    russian_to_english = russian_to_english_notes(vocab)
    write_anki_import_file(Path("/Users/alex/tmp/russian_to_english.txt"), russian_to_english, include_tag_column=False)
    english_to_russian = english_to_russian_notes(vocab)
    write_anki_import_file(Path("/Users/alex/tmp/english_to_russian.txt"), english_to_russian, include_tag_column=False)

def create_vocab_10000_two_sided_deck(force: bool):
    vocab = read_vocab_10000(force=force)
    notes = vocab_10000_notes(vocab)
    write_anki_import_file(Path("/Users/alex/tmp/vocab_10000.txt"), notes, include_tag_column=False)

def create_declinable_notes():
    notes = []
    for sample in SampleAdjective.samples():
        notes += adjective_notes(sample)
    for sample in SampleNoun.samples():
        notes += noun_notes(sample)
    write_anki_import_file(Path("/Users/alex/tmp/declinables.txt"), notes, include_tag_column=False)


if __name__ == '__main__':
    create_declinable_notes()
