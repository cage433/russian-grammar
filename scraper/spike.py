from pathlib import Path
from time import sleep

from bs4 import BeautifulSoup, Tag
import requests

from scraper.conjugation_parser import ConjugationParser


def file_contents():
    with open('/scraper/test_resources/scraped_pages/авторизовывать.html', 'rt', newline='') as f:
        return f.read()

def parse_file():
    text = file_contents()
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.body.find("div", {"class": 'NavHead'})
    print(divs.contents[-1])
    table = soup.body.find("div", {"class": 'NavContent'})
    rows = table.find_all('tr')
    for row in rows:
        # print(row.contents)
        texts = [
            c.text.strip() for c in row.contents
            if isinstance(c, Tag)
        ]
        print(texts)

def query_pages_for_verb(verb):
    # print(f"Asking for response for verb {verb}")
    url = f"https://en.wiktionary.org/wiki/{verb}#Conjugation.php"
    resp = requests.get(
        url,
        params={}
    ).text
    return resp

def extract_verb_data():
    with open(Path(__file__).parent.parent / 'resources' / 'verbs.txt', 'rt', newline='', buffering=1) as fw:
        verbs = fw.read().splitlines()

    for i, row in enumerate(verbs[177:200]):
        sleep(0.1)
        verb = row.split(' ')[2]
        print(f"Extracting data for verb {i}, {verb}")
        text = query_pages_for_verb(verb)
        soup = BeautifulSoup(text, 'html.parser')
        ConjugationParser(soup).parse_conjugation_from_soup

if __name__ == '__main__':
    extract_verb_data()