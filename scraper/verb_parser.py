from pathlib import Path

from bs4 import BeautifulSoup, Tag, PageElement

from utils.types import checked_type, checked_list_type


class VerbDetails:
    def __init__(self, infinitive: str):
        self.infinitive: str = checked_type(infinitive, str)

EXPECTED_LANGUAGES=[
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

class VerbSubSection:
    def __init__(self, tag: Tag, section: list[PageElement]):
        self.tag: Tag = checked_type(tag, Tag)
        self.section = checked_list_type(section, PageElement)

    @property
    def section_name(self) -> str:
        return self.tag.contents[0].text

class VerbParser:
    def __init__(self, verb: str, html: str):
        self.verb: str = checked_type(verb, str)
        self.html: str = checked_type(html, str)

    def is_heading(self, element, level):
        if isinstance(element, Tag) and element.has_attr("class") and element.attrs["class"] == ["mw-heading", f"mw-heading{level}"]:
            return True
        return False

    def extract_russian_elements(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        contents = soup.find_all(class_="mw-content-ltr mw-parser-output")
        if len(contents) != 1:
            raise ValueError(f"Unexpected content for {self.verb}")
        content = contents[0]
        language_headings = content.find_all(class_="mw-heading mw-heading2")
        parents = set(l.parent for l in language_headings)
        if not len(parents) == 1:
            raise ValueError(f"Unexpected parents")
        parent = list(parents)[0].extract()
        language_headings2 = [c for c in parent.contents if self.is_heading(c, level=2)]
        if language_headings != language_headings2:
            raise ValueError(f"Unexpected headings")
        russian_heading = [h for h in language_headings if h.contents[0].text == "Russian"][0]
        russian_stuff = []
        for item in russian_heading.next_siblings:
            if item in language_headings:
                break
            russian_stuff.append(item)
        return russian_stuff

    def group_into_sections(self, russian_stuff) -> list[VerbSubSection]:
        current_section = []
        current_heading = None
        headings_and_sections = []
        for element in russian_stuff:
            if self.is_heading(element, level=3) or self.is_heading(element, level=4):
                if current_heading is not None:
                    headings_and_sections.append(
                        VerbSubSection(current_heading, current_section)
                    )
                current_heading = element
                current_section = []
            else:
                current_section.append(element)
        return headings_and_sections

    def heading_title(self, tag: Tag):
        return tag.contents[0].text

    def parse(self):
        russian_stuff = self.extract_russian_elements()
        sub_sections = self.group_into_sections(russian_stuff)
        for ss in sub_sections:
            print(f"{ss.section_name} - {len(ss.section)} - {[type(x) for x in ss.section]}")
        return sub_sections

    @staticmethod
    def from_file(path: Path):
        with open(path) as p:
            html = p.read()
        return VerbParser(path.name, html)

if __name__ == '__main__':
    paths = Path("/Users/alex/repos/russian-grammar/scraper/verbs/").glob("*.html")
    for i_path, path in enumerate(list(paths)[:100]):
        verb = path.name
        parser = VerbParser.from_file(path)
        print("\n\n*****************")
        print(f"Parsing {i_path}, {path.name}")
        more_langs = parser.parse()

