import shelve
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag, PageElement, NavigableString
from more_itertools.recipes import flatten

from grammar.conjugation import Conjugation
from wikipedia.verb.verb_identifier import VerbIdentifier
from wikipedia.verb.verb_definition import QuoteAndTranslation, VerbDefinition
from wikipedia.wikipedia_verb_info import WikipediaVerbInfo
from scraper.conjugation_parser import ConjugationParser
from utils.types import checked_type, checked_list_type


class VerbDetails:
    def __init__(self, infinitive: str):
        self.infinitive: str = checked_type(infinitive, str)


EXPECTED_LANGUAGES = [
    "Bulgarian",
    "Central Mansi",
    "Erzya",
    "Komi-Yazva",
    "Macedonian",
    "Moksha",
    "Nivkh",
    "Old Church Slavonic",
    "Old East Slavic",
    "Old Novgorodian",
    "Old Ruthenian",
    "Russian",
    "Serbo-Croatian",
    "Udmurt",
    "Ukrainian",
]


class ParserUtils:
    @staticmethod
    def is_tag_of_class(element: PageElement, classes: list[str]) -> bool:
        if isinstance(element, Tag) and element.has_attr("class"):
            return set(element.attrs["class"]) == set(classes)
        return False

    def is_tag_with_class(element: PageElement, class_: str) -> bool:
        if isinstance(element, Tag) and element.has_attr("class"):
            return class_ in element.attrs["class"]
        return False

    @staticmethod
    def is_new_line(element: PageElement) -> bool:
        return isinstance(element, NavigableString) and element.text == '\n'

    @staticmethod
    def is_new_line_ish(element: PageElement) -> bool:
        if ParserUtils.is_new_line(element):
            return True
        return isinstance(element, NavigableString) and element.text == '.\n'

    @staticmethod
    def single_element(elements: list[any]) -> any:
        if len(elements) == 1:
            return elements[0]

        raise ValueError(f"Expected a single elements, got {elements}")

    @staticmethod
    def maybe_single_element(elements: list[any]) -> Optional[any]:
        if len(elements) == 1:
            return elements[0]
        if len(elements) == 0:
            return None

        raise ValueError(f"Expected 0 or 1 elements, got {elements}")

    @staticmethod
    def is_heading(element: PageElement, level: int) -> bool:
        if isinstance(element, Tag) and element.has_attr("class") and element.attrs["class"] == ["mw-heading",
                                                                                                 f"mw-heading{level}"]:
            return True
        return False

    def is_heading_in_range(element: PageElement, low_level: int, high_level: int) -> bool:
        return any(ParserUtils.is_heading(element, level) for level in range(low_level, high_level + 1))

    @staticmethod
    def heading_title(tag: Tag):
        return tag.contents[0].text

class QuoteAndTranslationParser:
    @staticmethod
    def from_element(tag: Tag) -> 'list[QuoteAndTranslation]':
        sub_tags = [t for t in tag.contents if isinstance(t, Tag)]
        result = []
        for t in sub_tags:

            quotations = t.find_all(class_="e-quotation")
            quotations += t.find_all(class_="e-example")
            translations = t.find_all(class_="e-translation")
            if len(quotations) == 1 and len(translations) >= 1:
                result.append(QuoteAndTranslation(quotations[0].text, translations[-1].text))
        return result


class VerbDefinitionParser:
    @staticmethod
    def from_tag(tag: Tag):
        contents = []
        for c in tag.contents:
            if isinstance(c, Tag) and c.name == 'style':
                continue
            contents.append(c)
        definition_elements = []
        for e in contents:
            if ParserUtils.is_new_line_ish(e):
                break
            if e.text.endswith('\n'):
                definition_elements.append(e)
                break
            definition_elements.append(e)

        quote_elements = contents[len(definition_elements):]

        if len(quote_elements) == 0:
            text = tag.text
            if text.startswith("passive of"):
                # remove transliteration
                terms = text.split(" ")
                text = " ".join(terms[:3])
            return VerbDefinition(text, quotes=[])
        else:
            texts = [t.text for t in definition_elements]
            text = "".join(texts)
            quote_tags = [t for t in quote_elements if isinstance(t, Tag)]
            quotes_and_translations = flatten([QuoteAndTranslationParser.from_element(tag) for tag in quote_tags])
            return VerbDefinition(text, list(quotes_and_translations))


class VerbIdentifierParser:
    @staticmethod
    def identifier(section: list[PageElement]) -> VerbIdentifier:
        return VerbIdentifier(
            VerbIdentifierParser.infinitive(section),
            VerbIdentifierParser.aspect(section)
        )

    @staticmethod
    def infinitive(section: list[PageElement]) -> str:
        potential_matches = flatten(s.find_all(class_="Cyrl") for s in section if isinstance(s, Tag))

        exact_matches = [c for c in potential_matches
                         if ParserUtils.is_tag_of_class(c, ["Cyrl", "headword"])
                         ]
        if not len(exact_matches) == 1:
            raise ValueError(f"Couldn't find infinitive, exact matches is {exact_matches}")
        return exact_matches[0].text.strip()


    @staticmethod
    def aspect(section: list[PageElement]) -> str:
        matches = list(flatten(s.find_all(class_="gender") for s in section if isinstance(s, Tag)))
        if len(matches) > 0:
            return matches[0].text
        raise ValueError("No aspect found")


class VerbCorrespondentsParser:
    @staticmethod
    def correspondents(tag: Tag) -> list[str]:
        potential_matches = tag.find_all(class_="Cyrl")
        exact_matches = [c for c in potential_matches if ParserUtils.is_tag_of_class(c, ["Cyrl"])]
        return [c.text.strip() for c in exact_matches]

class VerbDefinitionsParser:
    @staticmethod
    def definitions(section: list[PageElement]) -> list[VerbDefinition]:
        defs = []
        for element in section:
            if isinstance(element, Tag):
                defs += element.find_all('li', recursive=False)
        return [VerbDefinitionParser.from_tag(f) for f in defs]



class VerbConjugationParser:
    @staticmethod
    def parse(section: list[PageElement]) -> Conjugation:
        frames = []
        for s in section:
            if ParserUtils.is_tag_of_class(s, ["NavFrame"]):
                frames.append(s)
            elif isinstance(s, Tag):
                frames += s.find_all("div", {"class", 'NavFrame'})
        matching_frames = [f for f in frames if
                           "Conjugation of" in f.text and "fective" in f.text and "class" in f.text and "reform" not in f.text]
        conjugation_frame = matching_frames[0]
        parser = ConjugationParser(conjugation_frame)
        return parser.parse_conjugation_from_soup


class VerbAndDefinitionCollector:
    def __init__(self):
        self.collected: list[WikipediaVerbInfo] = []
        self.current_heading: Optional[Tag] = None
        self.current_section: list[PageElement] = []
        self.current_identifier: Optional[VerbIdentifier] = None
        self.current_correspondents: list[str] = []
        self.current_definitions: list[VerbDefinition] = []

        self.current_conjugation: Optional[Conjugation] = None
        self.current_derived_terms: list[str] = []
        self.current_related_terms: list[str] = []

    def process_current_state(self):
        if self.current_heading is not None:
            heading_title = ParserUtils.heading_title(self.current_heading)
            if heading_title == "Verb" or heading_title.startswith("Verb_"):
                if self.current_identifier is not None:
                    self.collect()
                self.set_current_identifier(VerbIdentifierParser.identifier(self.current_section))
                self.current_correspondents = VerbCorrespondentsParser.correspondents(self.current_section[1])
                self.current_definitions = VerbDefinitionsParser.definitions(self.current_section[1:])
            if heading_title == "Conjugation":
                self.set_current_conjugation(VerbConjugationParser.parse(self.current_section))
            if heading_title == "Derived terms":
                self.set_derived_terms([e.text
                                        for s in self.current_section if isinstance(s, Tag)
                                        for e in s.find_all(lang="ru")])
            if heading_title == "Related terms":
                self.set_related_terms([e.text
                                        for s in self.current_section if isinstance(s, Tag)
                                        for e in s.find_all(lang="ru")])
            self.current_heading = None
            self.current_section = []

    def process_element(self, element: PageElement):
        if ParserUtils.is_heading_in_range(element, low_level=3, high_level=5):
            if self.current_heading is not None:
                self.process_current_state()
            self.current_heading = element
            self.current_section = []
        if not ParserUtils.is_new_line(element):
            self.current_section.append(element)

    def collect(self):
        assert self.current_identifier is not None, "Have no current identifier"
        assert self.current_conjugation is not None, "Have no current conjugation"
        self.collected.append(
            WikipediaVerbInfo(
                self.current_identifier,
                self.current_correspondents,
                self.current_conjugation,
                self.current_definitions,
                self.current_derived_terms,
                self.current_related_terms
            )
        )
        self.current_identifier = None
        self.current_correspondents = []
        self.current_conjugation = None
        self.current_definitions = []
        self.current_derived_terms = []
        self.current_related_terms = []

    def set_current_identifier(self, identifier: VerbIdentifier):
        if self.current_identifier is not None:
            self.collect()
        self.current_identifier = identifier

    def set_current_conjugation(self, conjugation: Conjugation):
        assert self.current_conjugation is None, "Already have conjugation"
        self.current_conjugation = conjugation

    def set_derived_terms(self, derived_terms: list[str]):
        # A few verbs have multiple derived verbs sections, so we don't fail if they already exist
        self.current_derived_terms += derived_terms

    def set_related_terms(self, related_terms: list[str]):
        # A few verbs have multiple related verbs sections, so we don't fail if they already exist
        self.current_related_terms += related_terms


class WikipediaVerbInfoParser:
    def __init__(self, verb: str, page_html: str):
        self.verb: str = checked_type(verb, str)
        self.page_html: str = checked_type(page_html, str)

    def _russian_section_page_elements(self) -> list[PageElement]:
        soup = BeautifulSoup(self.page_html, 'html.parser')
        content = ParserUtils.single_element(soup.find_all(class_="mw-content-ltr mw-parser-output"))
        language_headings = content.find_all(class_="mw-heading mw-heading2")
        russian_heading = ParserUtils.single_element([h for h in language_headings if h.contents[0].text == "Russian"])
        russian_stuff = []

        def is_heading_starting_with(item: PageElement, text: str) -> bool:
            return ParserUtils.is_heading(item, level=3) and item.text.startswith(text)

        for item in russian_heading.next_siblings:
            if item in language_headings:
                break
            # For each of these the second etymology is or no interest
            if self.verb in ["навести", "вырасти", "есть", "расти", "подать"] and is_heading_starting_with(item,
                                                                                                           text="Etymology 2"):
                break
            if self.verb in ["знать"] and is_heading_starting_with(item, text="Noun"):
                break
            russian_stuff.append(item)
        return russian_stuff

    def _from_page_elements(self, elements: list[PageElement]) -> 'list[WikipediaVerbInfo]':
        collector = VerbAndDefinitionCollector()
        checked_list_type(elements, PageElement)

        for element in elements:
            collector.process_element(element)
        collector.process_current_state()
        collector.collect()

        return collector.collected

    def parse(self) -> 'list[WikipediaVerbInfo]':
        russian_stuff = self._russian_section_page_elements()
        result = self._from_page_elements(russian_stuff)
        result = WikipediaVerbInfo.merge(result)
        return result

    @staticmethod
    def from_file(path: Path) -> 'list[WikipediaVerbInfo]':
        with open(path) as p:
            html = p.read()
        return WikipediaVerbInfoParser(path.stem, html).parse()


    SHELF_PATH = Path(__file__).parent / "_verb_info.shelf"

    @staticmethod
    def from_locally_downloaded_pages(force: bool) -> list[WikipediaVerbInfo]:
        path = Path(__file__).parent / "wikipedia_pages"
        key = "Verb Definitions"
        with shelve.open(str(WikipediaVerbInfoParser.SHELF_PATH)) as shelf:
            if key not in shelf or force:
                html_files = list(path.glob('*.html'))
                verbs_and_definitions = []
                for i, f in enumerate(html_files):
                    print(f"Processing {i}, {f.stem}")
                    verbs_and_definitions += WikipediaVerbInfoParser.from_file(f)
                shelf[key] = verbs_and_definitions
            return shelf[key]

if __name__ == '__main__':
    path = Path(__file__).parent / "wikipedia_pages" / "жать.html"
    verb_and_def = WikipediaVerbInfoParser.from_file(path)
    from scripts.write_verb_anki_deck import verb_as_text_row
    text_row = verb_as_text_row(verb_and_def[0])
    print(text_row)
    # verbs_and_definitions = WikipediaVerbInfoParser.from_locally_downloaded_pages(force=False)
    # for p in verbs_and_definitions:
    #     print(p.identifier.infinitive)

