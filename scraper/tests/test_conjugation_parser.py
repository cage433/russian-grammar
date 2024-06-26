from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from grammar.conjugation import Conjugation
from scraper.conjugation_parser import ConjugationParser


class ConjugationParserTestCase(TestCase):
    def test_can_parse_all_samples(self):
        scraped_pages = Path(__file__).parent.parent / 'test_resources' / 'scraped_pages'
        for page in scraped_pages.iterdir():
            with open(page) as p:
                text = p.read()
            soup = BeautifulSoup(text, 'html.parser')
            # Not throwing an exception is a good sign
            conj = ConjugationParser(soup).parse_conjugation_from_soup
            table = conj.to_table()
            conj2 = Conjugation.from_table(table)
            self.assertEqual(conj, conj2)
