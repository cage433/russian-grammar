from curses import wrapper
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Tag, PageElement, NavigableString
from more_itertools.recipes import flatten

from utils.types import checked_type, checked_list_type, checked_optional_type


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

    @staticmethod
    def build(tag: Tag, section: list[PageElement]) -> 'VerbSubSection':
        heading_title = VerbSubSection.heading_title(tag)
        print(heading_title)
        if heading_title == "Verb" or heading_title.startswith("Verb_"):
            return VerbAspectDefinitionAndExamples(tag, section)
        if heading_title == "Derived terms":
            return VerbDerivedTerms(tag, section)
        if heading_title == "Related terms":
            return VerbRelatedTerms(tag, section)
        return VerbSubSection(tag, section)


class QuoteAndTranslation:
    def __init__(self, quote: str, translation: str):
        self.quote: str = checked_type(quote, str)
        self.translation: str = checked_type(translation, str)

    def __str__(self):
        return f"{self.quote} -- {self.translation}"

    def __repr__(self):
        return self.__str__()

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


class VerbDefinition:
    def __init__(self, meaning: str, quotes: list[QuoteAndTranslation]):
        self.meaning: str = checked_type(meaning, str)
        self.quotes: list[QuoteAndTranslation] = checked_list_type(quotes, QuoteAndTranslation)

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
            quotes_and_translations = flatten([QuoteAndTranslation.from_element(tag) for tag in quote_tags])
            return VerbDefinition(text, list(quotes_and_translations))


class VerbAspectDefinitionAndExamples(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name.startswith("Verb"):
            raise ValueError("Expected verb section")

    @property
    def infinitive(self) -> str:
        potential_matches = flatten(s.find_all(class_="Cyrl") for s in self.section)

        exact_matches = [c for c in potential_matches
                         if ParserUtils.is_tag_of_class(c, ["Cyrl", "headword"])
                         ]
        if not len(exact_matches) == 1:
            raise ValueError(f"Couldn't find infinitive, exact matches is {exact_matches}")
        return exact_matches[0].text.strip()

    @property
    def aspect(self) -> str:
        matches = list(flatten(s.find_all(class_="gender") for s in self.section))
        if len(matches) > 0:
            return matches[0].text
        raise ValueError("No aspect found")

    @property
    def correspondents(self) -> list[str]:
        potential_matches = self.section[0].find_all(class_="Cyrl")
        exact_matches = [c for c in potential_matches if ParserUtils.is_tag_of_class(c, ["Cyrl"])]
        return [c.text.strip() for c in exact_matches]

    @property
    def definitions(self):
        defs = self.section[1].find_all('li', recursive=False)
        return [VerbDefinition.from_tag(f) for f in defs]


class VerbDerivedTerms(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name == "Derived terms":
            raise ValueError("Expected derived terms")
        self.derived_terms = [e.text
                              for s in section if isinstance(s, Tag)
                              for e in s.find_all(lang="ru")]
        # # Ignore (e.g.) any notes sections
        # if len(section) == 1:
        #     wrapper = section[0]
        # else:
        #     wrapper = ParserUtils.single_element(
        #         list(s for s in section if ParserUtils.is_tag_with_class(s, "list-switcher-wrapper"))
        #     )
        # self.derived_terms = [e.text for e in wrapper.find_all(lang="ru")]

class VerbRelatedTerms(VerbSubSection):
    def __init__(self, heading: Tag, section: list[PageElement]):
        super().__init__(heading, section)
        if not self.section_name == "Related terms":
            raise ValueError("Expected related terms")
        self.related_terms = [e.text
                              for s in section if isinstance(s, Tag)
                              for e in s.find_all(lang="ru")]

class VerbParser:
    def __init__(self, verb: str, html: str):
        self.verb: str = checked_type(verb, str)
        self.html: str = checked_type(html, str)

    def is_heading(self, element: PageElement, level: int) -> bool:
        if isinstance(element, Tag) and element.has_attr("class") and element.attrs["class"] == ["mw-heading",
                                                                                                 f"mw-heading{level}"]:
            return True
        return False

    def extract_elements_from_russian_section_in_page(self) -> list[PageElement]:
        soup = BeautifulSoup(self.html, 'html.parser')
        content = ParserUtils.single_element(soup.find_all(class_="mw-content-ltr mw-parser-output"))
        def get_language_headings():
            headings = content.find_all(class_="mw-heading mw-heading2")
            parent = ParserUtils.single_element(list(set(l.parent for l in headings))).extract()
            headings_check = [c for c in parent.contents if self.is_heading(c, level=2)]
            if headings != headings_check:
                raise ValueError(f"Unexpected headings")
            return headings
        language_headings = content.find_all(class_="mw-heading mw-heading2")
        russian_heading = ParserUtils.single_element([h for h in language_headings if h.contents[0].text == "Russian"])
        russian_stuff = []
        for item in russian_heading.next_siblings:
            if item in language_headings:
                break
            if self.is_heading(item, level=3) and item.text.startswith("Etymology 2"):
                break
            russian_stuff.append(item)
        return russian_stuff

    def group_into_sections(self, elements: list[PageElement]) -> list[VerbSubSection]:
        checked_list_type(elements, PageElement)
        current_section = []
        current_heading: Optional[Tag] = None
        headings_and_sections = []
        for element in elements:
            if self.is_heading(element, level=3) or self.is_heading(element, level=4):
                if current_heading is not None:
                    headings_and_sections.append(
                        VerbSubSection.build(current_heading, current_section)
                    )
                current_heading = element
                current_section = []
                continue
            if ParserUtils.is_new_line(element):
                continue
            current_section.append(element)
        if current_heading is not None:
            headings_and_sections.append(
                VerbSubSection.build(current_heading, current_section)
            )
        return headings_and_sections

    def parse(self):
        russian_stuff = self.extract_elements_from_russian_section_in_page()
        sub_sections = self.group_into_sections(russian_stuff)
        for ss in [s for s in sub_sections if isinstance(s, VerbAspectDefinitionAndExamples)]:
            print(f"{ss.infinitive}, {ss.aspect}, {ss.correspondents}")
            for definition in ss.definitions:
                print(definition.meaning)
                for q in definition.quotes:
                    print(q)

        for ss in [s for s in sub_sections if isinstance(s, VerbDerivedTerms)]:
            print("Derived terms")
            for d in ss.derived_terms:
                print(f"\t{d}")
        for ss in [s for s in sub_sections if isinstance(s, VerbRelatedTerms)]:
            print("Related terms")
            for d in ss.related_terms:
                print(f"\t{d}")
        return sub_sections

    @staticmethod
    def from_file(path: Path):
        with open(path) as p:
            html = p.read()
        return VerbParser(path.name, html)


if __name__ == '__main__':
    paths = Path("/Users/alex/repos/russian-grammar/scraper/verbs/").glob("*.html")
    for i_path, path in enumerate(list(paths)):
        verb = path.name
        parser = VerbParser.from_file(path)
        print("\n\n*****************")
        print(f"Parsing {i_path}, {path.name}")
        more_langs = parser.parse()
