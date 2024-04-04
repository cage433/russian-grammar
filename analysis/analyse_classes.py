import re
from pathlib import Path

from grammar.conjugation import Conjugation
from grammar.conjugation_data import read_conjugations, verbs_matching_zaliznyak_class
from utils.utils import group_into_dict, sanitize_text


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

def report_on_class(short_class: str, force: bool):
    conjugations = verbs_matching_zaliznyak_class(short_class, stem_filter=None, force=force)
    infinitives_sans_reflexive = [sanitize_text(c.infinitive).replace("ся", "") for c in conjugations]
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
    print("classes")
    report_on_class_names(force=False)
    print("stresses")
    report_on_short_stresses(force=False)
    report_on_class('16', force=False)
    # notes = []
    # for stem in ["жить", "плыть", "слыть"]:
    #     notes.extend(create_notes_for('16', stem, force=False))

    # conjugations = read_conjugations(force=False)
    # cs = [c for c in conjugations if sanitize_text(c.infinitive) in ["гулять", "погулять"]]
    # notes = [
    #     n
    #     for c in cs
    #     for n in notes_for_conjugation(c, stem=None)
    # ]
    # print(f"Have {len(notes)} notes")
    # write_anki_import_file(Path("/Users/alex/tmp/verbs.txt"), notes)
