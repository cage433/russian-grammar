from pathlib import Path
from typing import Optional

from more_itertools import flatten

from grammar.conjugation import Aspect, PresentOrFutureConjugation
from scraper.wikipedia_verb_info_parser import WikipediaVerbInfoParser
from utils.utils import group_into_dict
from wikipedia.verb.verb_definition import VerbDefinition
from wikipedia.wikipedia_verb_info import WikipediaVerbInfo


def remove_new_lines(text: str) -> str:
    return text.replace(";", ",").replace('\n', "")


def clean(text: str) -> str:
    return text.replace(";", ",").replace('\n', "<br>")


def list_term(term: str) -> str:
    return f"<li>{clean(term)}</li>"


def ordered_list(terms: list[str]) -> str:
    li_elements = [list_term(t) for t in terms]
    li_term = "".join(li_elements)
    return f"<ul>{li_term}</ul>"


def definitions_field(definitions: list[VerbDefinition]) -> str:
    return ordered_list([d.meaning for d in definitions])


def examples_field(definitions: list[VerbDefinition]) -> str:
    terms = []
    for d in definitions:
        for q in d.quotes:
            quote_and_trans = f"<em>{q.quote}</em> - {q.translation}"
            terms.append(quote_and_trans)
    if len(terms) == 0:
        return ""
    heading = """<p style="text-align:left"><strong>Examples:</strong></p>"""
    return f"{heading}{ordered_list(terms)}"


def correspondents_field(verb_aspect: str, correspondents: list[str]) -> str:
    if len(correspondents) == 0:
        return ""
    list_text = ", ".join([f"<em>{c}</em>" for c in correspondents])
    if verb_aspect == Aspect.PERFECTIVE:
        correspondent_aspect = "impf."
    elif verb_aspect == Aspect.IMPERFECTIVE:
        correspondent_aspect = "perf."
    else:
        raise ValueError(f"Unexpected aspect {verb_aspect}")
    return f"({correspondent_aspect} {list_text})"


def conjugation_field(tense: PresentOrFutureConjugation) -> str:
    def term(text: Optional[str]) -> str:
        if text is None:
            return "-"
        return f"<em>{text}</em>"
    def table_row(name, text):
        return f"<tr><td>{name}</td><td>{term(text)}</td></tr>"
    rows = [
        table_row(n, s)
        for n, s in [
            ("1s ", tense.first_person_singular),
            ("2s ", tense.second_person_singular),
            ("3p ", tense.third_person_plural)
        ]
    ]
    rows_text = "".join(rows)
    colgroup = """<colgroup> <col span="1" style="width: 30%"> <col span="1" style="width: 70%"></colgroup>"""
    return f"<table>{colgroup}<tbody>{rows_text}</tbody></table>"


def verb_as_text_row(infinitive: str, aspect: str, short_class: str, short_stress: str,
                     tense: PresentOrFutureConjugation, verbs: list[WikipediaVerbInfo]):
    if short_class == "irreg":
        short_class_for_deck = short_class
    else:
        short_class_for_deck = f"{int(short_class):02d}"
    verb_class = short_class + short_stress
    deck = f"3000 Verbs::{short_class_for_deck}::{short_stress}"
    merged_definitions = list(flatten(v.definitions for v in verbs))
    merged_correspondents = list(set(flatten(v.correspondents for v in verbs)))

    terms = [
        "3000 Verbs",
        deck,
        infinitive,
        Aspect.short_aspect(aspect),
        verb_class,
        conjugation_field(tense),
        definitions_field(merged_definitions),
        examples_field(merged_definitions),
        correspondents_field(aspect, merged_correspondents)
    ]
    return ";".join(terms)


def write_anki_import_file(file_path: Path, verbs: list[WikipediaVerbInfo]):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")

        grouped_verbs = group_into_dict(verbs, lambda verb: (
            verb.infinitive, verb.aspect, verb.conjugation.short_class, verb.conjugation.short_stress,
            verb.conjugation.present_or_future))
        for (infinitive, aspect, short_class, short_stress, present_or_future), vs in grouped_verbs.items():
            f.write(verb_as_text_row(infinitive, aspect, short_class, short_stress, present_or_future, vs) + "\n")


def create_deck(z_class: Optional[any]):
    verbs = WikipediaVerbInfoParser.from_locally_downloaded_pages(force=False)
    if z_class is not None:
        verbs = [v for v in verbs if v.conjugation.short_class == f"{z_class}"]
        path = Path(f"/Users/alex/tmp/verbs_{z_class}.csv")
    else:
        path = Path(f"/Users/alex/tmp/verbs.csv")
    write_anki_import_file(path, verbs)



if __name__ == '__main__':
    create_deck(z_class=None)
