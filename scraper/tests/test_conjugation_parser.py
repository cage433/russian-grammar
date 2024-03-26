from pathlib import Path
from unittest import TestCase

from bs4 import BeautifulSoup

from scraper.conjugation_parser import ConjugationParser


class ConjugationParserTestCase(TestCase):
    def test_can_parse_all_samples(self):
        scraped_pages = Path(__file__).parent.parent / 'test_resources' / 'scraped_pages'
        for page in scraped_pages.iterdir():
            with open(page) as p:
                text = p.read()
            soup = BeautifulSoup(text, 'html.parser')
            conjugaton = ConjugationParser.parse_conjugation_from_soup(soup)
            print(conjugaton)
