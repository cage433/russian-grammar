import unicodedata
from pathlib import Path
from typing import List, Optional
import re
import shelve
from grammar.conjugation import Conjugation, Aspect
from utils.csv_utils import read_csv_file
from utils.utils import group_into_dict

CONJUGATIONS_PATH = Path(__file__).parent.parent / 'resources' / 'conjugations'
SHELF_PATH = Path(__file__).parent / "_conjugations.shelf"


def read_conjugations(force: bool) -> List[Conjugation]:
    key = "Conjugations"
    with shelve.open(str(SHELF_PATH)) as shelf:
        if key not in shelf or force:
            csv_files = list(CONJUGATIONS_PATH.rglob('*.csv'))
            conjugations = []
            for f in csv_files:
                table = read_csv_file(f)
                conjugations.append(Conjugation.from_table(table))
            shelf[key] = conjugations
        return shelf[key]


def report_by_class(force: bool):
    m = re.compile(r'(\d+[abc])')
    conjugations = read_conjugations(force)

    def short_name(c: Conjugation):
        if a := m.match(c.verb_type.zaliznyak_class.class_name):
            return a.groups()[0]
        return ""

    by_class = group_into_dict(
        conjugations,
        short_name
    )
    classes = sorted(by_class.keys())
    for c in classes:
        print(f"{c}: {len(by_class[c])}")


def sanitize(word):
    return ''.join(filter(
        lambda x: unicodedata.category(x) != 'Mn' and x not in ['△', '*'],
        unicodedata.normalize('NFD', word)
    ))


def verbs_matching(short_class: str, stem_filter: Optional[str], force: bool):
    conjugations = read_conjugations(force)
    matching = [c for c in conjugations if c.verb_type.zaliznyak_class.short_class == short_class]
    if stem_filter is None:
        return matching

    reflexive_stem = stem_filter + "ся"
    matching_stem = [c for c in matching if
                     sanitize(c.infinitive).endswith(stem_filter) or sanitize(c.infinitive).endswith(
                         reflexive_stem)]
    return matching_stem


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


def translation_note(deck: str, c: Conjugation):
    return ";".join([
        "Basic (and reversed card)",
        deck,
        f"{c.infinitive};TODO"
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


def notes_for_conjugation(c: Conjugation, stem: Optional[str]):
    short_class = c.verb_type.zaliznyak_class.short_class
    if len(short_class) == 1:
        short_class = "0" + short_class
    if stem is not None:
        verb_deck = f"Russian Verbs::{short_class}::{stem}"
    else:
        verb_deck = f"Russian Verbs::{short_class}"
    definitions_deck = "Russian Verbs::Definitions"

    return [
        conjugation_note(verb_deck, c),
        verb_type_note(verb_deck, c),
        translation_note(definitions_deck, c)
    ]


def create_notes_for(short_class: str, stem: str, force: bool):
    matching = verbs_matching(short_class, stem_filter=stem, force=force)
    return [
        n for n in [notes_for_conjugation(c, stem) for c in matching]
    ]


def report_on_class(short_class: str, force: bool):
    conjugations = verbs_matching(short_class, stem_filter=None, force=force)
    infinitives_sans_reflexive = [sanitize(c.infinitive).replace("ся", "") for c in conjugations]
    reversed_infinitives = [s[::-1] for s in infinitives_sans_reflexive]
    for s in sorted(list(set(reversed_infinitives))):
        print(s)


def report_on_class_names(force: bool):
    conjugations = read_conjugations(force=force)
    classes = sorted(list({c.verb_type.zaliznyak_class.class_name for c in conjugations}))
    for c in classes:
        print(c)


def report_on_short_stresses(force: bool):
    conjugations = read_conjugations(force=force)
    stresses = sorted(list({c.verb_type.zaliznyak_class.short_stress for c in conjugations}))
    for c in stresses:
        print(c)


if __name__ == '__main__':
    # print("classes")
    # report_on_class_names(force=False)
    # print("stresses")
    # report_on_short_stresses(force=False)
    # report_on_class('16', force=False)
    # notes = []
    # for stem in ["жить", "плыть", "слыть"]:
    #     notes.extend(create_notes_for('16', stem, force=False))

    conjugations = read_conjugations(force=False)
    cs = [c for c in conjugations if sanitize(c.infinitive) in ["пообедать", "обедать"]]
    notes = [
        n
        for c in cs
        for n in notes_for_conjugation(c, stem=None)
    ]
    print(f"Have {len(notes)} notes")
    write_anki_import_file(Path("/Users/alex/tmp/verbs.txt"), notes)
