from pathlib import Path
from time import sleep
from typing import List

from bs4 import BeautifulSoup, Tag
import requests

from scraper.conjugation_parser import ConjugationParser
from utils.csv_utils import write_csv_file


def wiktionary_verb_entry(verb):
    url = f"https://en.wiktionary.org/wiki/{verb}"
    resp = requests.get(
        url,
        params={}
    ).text
    return resp


def verb_list() -> List[str]:
    with open(Path(__file__).parent.parent / 'resources' / 'verbs.txt', 'rt', newline='', buffering=1) as fw:
        lines = fw.read().splitlines()
        return [line.split(' ')[2] for line in lines]


def persist_conjugations(output_dir: Path, overwrite: bool):
    error_file = output_dir / 'errors.txt'
    verbs = verb_list()
    num_verbs = len(verbs)
    for i, verb in enumerate(verbs):
        sleep(0.1)
        print(f"Processing verb no. {i + 1} of {num_verbs}, {verb}")
        try:
            prefix = verb[:2]
            verb_dir = output_dir / prefix
            if not verb_dir.exists():
                verb_dir.mkdir()
            csv_path = verb_dir / f"{verb}.csv"
            if csv_path.exists() and not overwrite:
                continue
            soup = BeautifulSoup(wiktionary_verb_entry(verb), 'html.parser')
            conjugation = ConjugationParser(soup).parse_conjugation_from_soup
            if conjugation is None:
                print(f"Conjugation is None for verb {i}, {verb}")
                with open(error_file, 'a') as ef:
                    ef.write(f"{verb}\n")
                continue
            table = conjugation.to_table()
            write_csv_file(csv_path, table)
        except Exception as e:
            print(f"Error extracting data for verb {i}, {verb}")
            with open(error_file, 'a') as ef:
                ef.write(f"{verb}\n")




def parse_errors():
    with open(Path(__file__).parent.parent / 'resources' / 'conjugations' / 'errors.txt', 'rt') as ef:
        verbs = ef.read().splitlines()
    for verb in verbs:
        print(f"Processing verb {verb}")
        soup = BeautifulSoup(wiktionary_verb_entry(verb), 'html.parser')
        conjugation = ConjugationParser(soup).parse_conjugation_from_soup


def scrape_all_verbs(overwrite: bool = False):
    output_dir = Path(__file__).parent.parent / 'resources' / 'conjugations'
    if not output_dir.exists():
        output_dir.mkdir()
    persist_conjugations(output_dir, overwrite)


if __name__ == '__main__':
    scrape_all_verbs(overwrite=True)
