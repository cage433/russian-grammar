from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag, PageElement, NavigableString
from more_itertools.recipes import flatten

from grammar.conjugation import Conjugation
from language.verb.verb_info import QuoteAndTranslation, VerbDefinition, VerbDefinitionAndExamples
from language.verb_and_definitions import VerbAndDefinitions
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


class VerbSubSection:
    def __init__(self, heading: Tag, section: list[PageElement]):
        self.heading: Tag = checked_type(heading, Tag)
        self.section = checked_list_type(section, PageElement)

    @property
    def section_name(self) -> str:
        return self.heading.contents[0].text

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
        contents = tag.contents
        i_new_lines = [i for i in range(len(contents)) if ParserUtils.is_new_line_ish(contents[i])]
        if len(i_new_lines) == 0:
            text = tag.text
            if text.startswith("passive of"):
                # remove transliteration
                terms = text.split(" ")
                text = " ".join(terms[:3])
            return VerbDefinition(text, quotes=[])
        else:
            texts = [t.text for t in contents[:i_new_lines[0]]]
            text = "".join(texts)
            quote_tags = [t for t in contents[i_new_lines[0] + 1:] if isinstance(t, Tag)]
            quotes_and_translations = flatten([QuoteAndTranslationParser.from_element(tag) for tag in quote_tags])
            return VerbDefinition(text, list(quotes_and_translations))


class VerbDefinitionAndExamplesParser(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name.startswith("Verb"):
            raise ValueError("Expected verb section")

    def parse(self) -> VerbDefinitionAndExamples:
        return VerbDefinitionAndExamples(
            self.infinitive,
            self.aspect,
            self.correspondents,
            self.definitions
        )

    @property
    def infinitive(self) -> str:
        potential_matches = flatten(s.find_all(class_="Cyrl") for s in self.section if isinstance(s, Tag))

        exact_matches = [c for c in potential_matches
                         if ParserUtils.is_tag_of_class(c, ["Cyrl", "headword"])
                         ]
        if not len(exact_matches) == 1:
            raise ValueError(f"Couldn't find infinitive, exact matches is {exact_matches}")
        return exact_matches[0].text.strip()

    @property
    def aspect(self) -> str:
        matches = list(flatten(s.find_all(class_="gender") for s in self.section if isinstance(s, Tag)))
        if len(matches) > 0:
            return matches[0].text
        raise ValueError("No aspect found")

    @property
    def correspondents(self) -> list[str]:
        potential_matches = self.section[0].find_all(class_="Cyrl")
        exact_matches = [c for c in potential_matches if ParserUtils.is_tag_of_class(c, ["Cyrl"])]
        return [c.text.strip() for c in exact_matches]

    @property
    def definitions(self) -> list[VerbDefinition]:
        defs = self.section[1].find_all('li', recursive=False)
        return [VerbDefinitionParser.from_tag(f) for f in defs]


class VerbDerivedTerms(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name == "Derived terms":
            raise ValueError("Expected derived terms")
        self.derived_terms = [e.text
                              for s in section if isinstance(s, Tag)
                              for e in s.find_all(lang="ru")]


class VerbRelatedTerms(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name == "Related terms":
            raise ValueError("Expected related terms")
        self.related_terms = [e.text
                              for s in section if isinstance(s, Tag)
                              for e in s.find_all(lang="ru")]


class VerbConjugationParser(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        frames = []
        for s in self.section:
            if ParserUtils.is_tag_of_class(s, ["NavFrame"]):
                frames.append(s)
            elif isinstance(s, Tag):
                frames += s.find_all("div", {"class", 'NavFrame'})
        matching_frames = [f for f in frames if
                           "Conjugation of" in f.text and "fective" in f.text and "class" in f.text and "reform" not in f.text]
        self.conjugation_frame = matching_frames[0]
        parser = ConjugationParser(self.conjugation_frame)
        self.conjugation: Conjugation = parser.parse_conjugation_from_soup

    def parse(self) -> Conjugation:
        return self.conjugation


class VerbAndDefinitionCollector:
    def __init__(self):
        self.collected: list[VerbAndDefinitions] = []
        self.current_heading: Optional[Tag] = None
        self.current_section: list[PageElement] = []
        self.current_definition_and_examples: Optional[VerbDefinitionAndExamples] = None
        self.current_conjugation: Optional[Conjugation] = None
        self.current_derived_terms: list[str] = []
        self.current_related_terms: list[str] = []

    def process_current_state(self):
        if self.current_heading is not None:
            heading_title = VerbSubSection.heading_title(self.current_heading)
            print(heading_title)
            if heading_title == "Verb" or heading_title.startswith("Verb_"):
                if self.current_definition_and_examples is not None:
                    self.collect()
                self.set_current_definition(
                    VerbDefinitionAndExamplesParser(self.current_heading, self.current_section).parse())
            if heading_title == "Conjugation":
                self.set_current_conjugation(VerbConjugationParser(self.current_heading, self.current_section).parse())
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
        assert self.current_definition_and_examples is not None, "Have no current definition"
        assert self.current_conjugation is not None, "Have no current conjugation"
        self.collected.append(
            VerbAndDefinitions(
                self.current_definition_and_examples.infinitive,
                self.current_definition_and_examples.aspect,
                self.current_definition_and_examples.correspondents,
                self.current_conjugation,
                self.current_definition_and_examples.definitions,
                self.current_derived_terms,
                self.current_related_terms
            )
        )
        self.current_definition_and_examples = None
        self.current_conjugation = None
        self.current_derived_terms = []
        self.current_related_terms = []

    def set_current_definition(self, definition: VerbDefinitionAndExamples):
        if self.current_definition_and_examples is not None:
            self.collect()
        self.current_definition_and_examples = definition

    def set_current_conjugation(self, conjugation: Conjugation):
        assert self.current_conjugation is None, "Already have conjugation"
        self.current_conjugation = conjugation

    def set_derived_terms(self, derived_terms: list[str]):
        # A few verbs have multiple derived verbs sections, so we don't fail if they already exist
        self.current_derived_terms += derived_terms

    def set_related_terms(self, related_terms: list[str]):
        # A few verbs have multiple related verbs sections, so we don't fail if they already exist
        self.current_related_terms += related_terms


class VerbParser:
    def __init__(self, verb: str, html: str):
        self.verb: str = checked_type(verb, str)
        self.html: str = checked_type(html, str)

    def extract_elements_from_russian_section_in_page(self) -> list[PageElement]:
        soup = BeautifulSoup(self.html, 'html.parser')
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

    def group_into_sections(self, elements: list[PageElement]) -> 'list[VerbAndDefinitions]':
        collector = VerbAndDefinitionCollector()
        checked_list_type(elements, PageElement)

        for element in elements:
            collector.process_element(element)
        collector.process_current_state()
        collector.collect()

        return collector.collected

    def parse(self) -> 'list[VerbAndDefinitions]':
        russian_stuff = self.extract_elements_from_russian_section_in_page()
        result = self.group_into_sections(russian_stuff)
        return result

    @staticmethod
    def from_file(path: Path):
        with open(path) as p:
            html = p.read()
        return VerbParser(path.stem, html)


if __name__ == '__main__':
    paths = Path("/Users/alex/repos/russian-grammar/scraper/wikipedia_pages/").glob("*.html")
    for i_path, path in enumerate(list(paths)):
        verb = path.name
        parser = VerbParser.from_file(path)
        print("\n\n*****************")
        print(f"Parsing {i_path}, {path.name}")
        parsed = parser.parse()
        infs = [p.conjugation.infinitive for p in parsed]
        print(f"Parsed {infs}")
