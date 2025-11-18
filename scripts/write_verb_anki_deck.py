from pathlib import Path

from more_itertools import flatten

from scraper.wikipedia_verb_info_parser import WikipediaVerbInfoParser
from utils.utils import group_into_dict
from wikipedia.verb.verb_definition import VerbDefinition
from wikipedia.verb.verb_identifier import VerbIdentifier
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

def definitions_field(definitions: list[VerbDefinition])-> str:
    return ordered_list([d.meaning for d in definitions])

def examples_field(definitions: list[VerbDefinition])-> str:
    terms = []
    for d in definitions:
        for q in d.quotes:
            quote_and_trans = f"{q.quote} - {q.translation}"
            terms.append(quote_and_trans)
    if len(terms) == 0:
        return ""
    heading = """<p style="text-align:left"><strong>Examples:</strong></p>"""
    return f"{heading}{ordered_list(terms)}"

def correspondents_field(verb_aspect: str, correspondents: list[str])-> str:
    if len(correspondents) == 0:
        return ""
    list_text = ", ".join([f"<em>{c}</em>" for c in correspondents])
    if verb_aspect == "pf":
        correspondent_aspect = "impf."
    elif verb_aspect == "impf":
        correspondent_aspect = "perf."
    else:
        raise ValueError(f"Unexpected aspect {verb_aspect}")
    return f"({correspondent_aspect} {list_text})"

def verb_as_text_row(id: VerbIdentifier, short_class: str, short_stress: str, verbs: list[WikipediaVerbInfo]):
    verb_class = short_class + short_stress
    deck = f"Verbs::{short_class}::{short_stress}"
    merged_definitions = list(flatten(v.definitions for v in verbs))
    merged_correspondents = list(set(flatten(v.correspondents for v in verbs)))
    terms = [
        "Verbs",
        deck,
        id.infinitive,
        id.aspect,
        verb_class,
        definitions_field(merged_definitions),
        examples_field(merged_definitions),
        correspondents_field(id.aspect, merged_correspondents)
    ]
    return ";".join(terms)


def write_anki_import_file(file_path: Path, verbs: list[WikipediaVerbInfo]):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")
        grouped_verbs = group_into_dict(verbs, lambda verb: (verb.identifier, verb.conjugation.short_class, verb.conjugation.short_stress))
        for (id, short_class, short_stress), vs in grouped_verbs.items():
            f.write(verb_as_text_row(id, short_class, short_stress, vs) + "\n")


def create_deck():
    verbs = WikipediaVerbInfoParser.from_locally_downloaded_pages(force=False)
    verbs_14 = [v for v in verbs if v.conjugation.short_class == "14"]
    path = Path(f"/Users/alex/tmp/verbs_14.csv")
    write_anki_import_file(path, verbs_14)


if __name__ == '__main__':
    create_deck()
