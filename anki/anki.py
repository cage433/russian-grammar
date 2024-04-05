from pathlib import Path
from typing import List, Optional

from grammar.conjugation import Conjugation, Aspect
from grammar.conjugation_data import read_conjugations, verbs_matching_zaliznyak_class, find_conjugation
from utils.utils import sanitize_text

VERBS_DECK = "Russian Verbs"
VERB_DEFINITIONS_DECK = f"{VERBS_DECK}::Definitions"


def conjugation_note(deck: str, conjugation: Conjugation):
    terms = [t for t in conjugation.present_or_future.terms]
    if conjugation.verb_type.aspect == Aspect.PERFECTIVE:
        line = "Future<br>"
    else:
        line = "Present<br>"

    if any([t is None for t in terms]):
        labels = [
            "1s", "2s", "3s", "1p", "2p", "3p"
        ]
        terms = [f"{l}: {t}" for l, t in zip(labels, terms) if t is not None]
    line += "<br>".join(terms) + "<br><br>"

    terms = [t for t in conjugation.past.terms]
    if any([t is None for t in terms]):
        labels = [
            "M", "F", "N", "P",
        ]
        terms = [f"{l}: {t}" for l, t in zip(labels, terms) if t is not None]
    if terms:
        line += "Past<br>"
        line += "<br>".join(terms) + "<br><br>"

    return ";".join([
        "Basic",
        deck,
        f"Conjugate {conjugation.infinitive};{line}"
    ])


def translation_note(deck: str, russian_text: str):
    return ";".join([
        "Basic (and reversed card)",
        deck,
        f"{russian_text};TODO"
    ])


def translation_note_for_aspect_pair(deck: str, impf: Conjugation, perf: Conjugation):
    return ";".join([
        "Basic (and reversed card)",
        deck,
        f"{impf.infinitive} (pf. {perf.infinitive})<br>;TODO"
    ])


def verb_type_note(deck: str, c: Conjugation):
    line = c.verb_type.aspect
    if not c.verb_type.reflexive:
        if c.verb_type.transitive:
            line += " transitive"
        else:
            line += " intransitive"
    line += f" {c.verb_type.zaliznyak_class.short_class_and_stress}"
    return ";".join([
        "Basic",
        deck,
        f"Verb type of {c.infinitive};{line}"
    ])


def write_anki_import_file(file_path: Path, notes: List[str]):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")
        for n in notes:
            f.write(n + "\n")


def verb_notes_for_conjugation(c: Conjugation, stem: Optional[str]):
    short_class = c.verb_type.zaliznyak_class.short_class
    if len(short_class) == 1:
        short_class = "0" + short_class
    if stem is not None:
        verb_deck = f"{VERBS_DECK}::{short_class}::{stem}"
    else:
        verb_deck = f"{VERBS_DECK}::{short_class}"

    return [
        conjugation_note(verb_deck, c),
        verb_type_note(verb_deck, c),
    ]


def create_notes_for_conjugation(c: Conjugation, stem: Optional[str]):
    return verb_notes_for_conjugation(c, stem) + [
        translation_note(VERB_DEFINITIONS_DECK, c.infinitive)
    ]


def create_notes_for_aspect_pair(imperfective: Conjugation, perfective: Conjugation, include_translation: bool):
    if not imperfective.verb_type.aspect == Aspect.IMPERFECTIVE:
        raise ValueError(f"First verb must be imperfective, got {imperfective.infinitive}")
    if not perfective.verb_type.aspect == Aspect.PERFECTIVE:
        raise ValueError(f"Second verb must be perfective, got {perfective.infinitive}")
    notes = verb_notes_for_conjugation(imperfective, stem=None) \
        + verb_notes_for_conjugation(perfective, stem=None)
    if include_translation:
        notes.append(translation_note_for_aspect_pair(
            VERB_DEFINITIONS_DECK, imperfective, perfective))
    return notes


def create_notes_zaliznyak_category(short_class: str, stem: str, force: bool):
    matching = verbs_matching_zaliznyak_class(short_class, stem_filter=stem, force=force)
    return [
        n for n in [create_notes_for_conjugation(c, stem) for c in matching]
    ]


if __name__ == '__main__':
    notes = []
    for imperfective, perfective in [
        ("работать", "поработать"),
    ]:
        impf = find_conjugation(imperfective, force=False)
        perf = find_conjugation(perfective, force=False)
        notes.extend(create_notes_for_aspect_pair(impf, perf, include_translation=True))
    print(f"Have {len(notes)} notes")
    write_anki_import_file(Path("/Users/alex/tmp/verbs.txt"), notes)
