from pathlib import Path
from typing import List

from grammar.conjugation import Conjugation
from utils.csv_utils import read_csv_file


def read_conjugations(parent_dir: Path) -> List[Conjugation]:
    csv_files = list(parent_dir.rglob('*.csv'))
    conjugations = []
    for f in csv_files:
        table =read_csv_file(f)
        conjugations.append(Conjugation.from_table(table))
    print(len(conjugations))


if __name__ == '__main__':
    read_conjugations(Path(__file__).parent.parent / 'resources' / 'old_conjugations')