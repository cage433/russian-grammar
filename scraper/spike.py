from pathlib import Path
from time import sleep
from typing import List

from bs4 import BeautifulSoup, Tag
import requests

from scraper.conjugation_parser import ConjugationParser
from utils.csv_utils import write_csv_file


def wiktionary_verb_entry(verb):
    url = f"https://en.wiktionary.org/wiki/{verb}#Conjugation.php"
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
    for i, verb in enumerate(verb_list()[:10]):
        sleep(0.1)
        print(f"Processing verb no. {i}, {verb}")
        try:
            soup = BeautifulSoup(wiktionary_verb_entry(verb), 'html.parser')
            conjugation = ConjugationParser(soup).parse_conjugation_from_soup
            table = conjugation.to_table()
            prefix = verb[:2]
            verb_dir = output_dir / prefix
            if not verb_dir.exists():
                verb_dir.mkdir()
            csv_path = verb_dir / f"{verb}.csv"
            if overwrite or not csv_path.exists():
                write_csv_file(csv_path, table)
        except Exception as e:
            print(f"Error extracting data for verb {i}, {verb}")
            with open(error_file, 'a') as ef:
                ef.write(f"{verb}\n")
            raise e


if __name__ == '__main__':
    output_dir = Path(__file__).parent.parent / 'resources' / 'conjugations'
    if not output_dir.exists():
        output_dir.mkdir()
    persist_conjugations(output_dir, overwrite=False)
