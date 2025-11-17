from pathlib import Path

from scraper.wikipedia_verb_info_parser import WikipediaVerbInfoParser
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

def definitions_field(verb: WikipediaVerbInfo)-> str:
    return ordered_list([d.meaning for d in verb.definitions])

def examples_field(verb: WikipediaVerbInfo)-> str:
    terms = []
    for d in verb.definitions:
        for q in d.quotes:
            quote_and_trans = f"{q.quote} - {q.translation}"
            terms.append(quote_and_trans)
    if len(terms) == 0:
        return ""
    return f"<hr>{ordered_list(terms)}"

def verb_as_text_row(verb: WikipediaVerbInfo):
    verb_class = verb.conjugation.short_class + verb.conjugation.short_stress
    deck = f"Verbs::{verb.conjugation.short_class}::{verb.conjugation.short_stress}"
    terms = [
        "Verbs",
        deck,
        verb.identifier.infinitive,
        verb.identifier.aspect,
        verb_class,
        definitions_field(verb),
        examples_field(verb)
    ]
    return ";".join(terms)


def write_anki_import_file(file_path: Path, verbs: list[WikipediaVerbInfo]):
    with open(str(file_path), 'wt', newline='') as f:
        f.write("#separator:;\n")
        f.write("#notetype column:1\n")
        f.write("#deck column:2\n")
        for v in verbs:
            f.write(verb_as_text_row(v) + "\n")


def create_deck():
    verbs = WikipediaVerbInfoParser.from_locally_downloaded_pages(force=False)
    verbs_14 = [v for v in verbs if v.conjugation.short_class == "14"]
    path = Path(f"/Users/alex/tmp/verbs_14.csv")
    write_anki_import_file(path, verbs_14)


if __name__ == '__main__':
    create_deck()
