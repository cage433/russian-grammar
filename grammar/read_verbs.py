import re
import shelve
from pathlib import Path
from typing import List

from grammar.conjugation import Conjugation
from grammar.conjugation_data import read_conjugations
from utils.utils import strip_stress_marks

VERBS_TEXT = Path(__file__).parent.parent / 'resources' / 'verbs.txt'
SHELF_PATH = Path(__file__).parent / "_verbs.shelf"

def read_verbs_in_usage_order(force: bool = False) -> List[Conjugation]:
    key = "Verbs"
    with shelve.open(str(SHELF_PATH)) as shelf:
        if key not in shelf or force:
            conjugation_by_inf = {strip_stress_marks(c.infinitive): c for c in read_conjugations(force=force)}
            regex = re.compile(r'(\d+) +\d+\.\d+ (\w+) verb')
            verbs = []
            with open(VERBS_TEXT) as f:
                lines = [line.strip() for line in f.readlines()]
                n_missing = 0
                for i, line in enumerate(lines):
                    a = regex.match(line)
                    if a:
                        infinitive = a.groups()[1]
                        conj = conjugation_by_inf.get(infinitive)
                        if conj is not None:
                            verbs.append(conj)
                    else:
                        raise ValueError(f"Bad line {line}")
            shelf[key] = verbs
        return shelf[key]



if __name__ == '__main__':
    verbs_in_usage_order = read_verbs_in_usage_order()
    by_infinitive = {strip_stress_marks(c.infinitive): c for c in verbs_in_usage_order}
    print(by_infinitive["хотеть"])
    print(f"Read {len(verbs_in_usage_order)} verbs")