import shelve
from pathlib import Path
from typing import List, Optional

from grammar.conjugation import Conjugation
from utils.csv_utils import read_csv_file
from utils.utils import sanitize_text

CONJUGATIONS_CSV_PATH = Path(__file__).parent.parent / 'resources' / 'conjugations'
SHELF_PATH = Path(__file__).parent / "_conjugations.shelf"


def read_conjugations(force: bool) -> List[Conjugation]:
    key = "Conjugations"
    with shelve.open(str(SHELF_PATH)) as shelf:
        if key not in shelf or force:
            csv_files = list(CONJUGATIONS_CSV_PATH.rglob('*.csv'))
            conjugations = []
            for f in csv_files:
                table = read_csv_file(f)
                conjugations.append(Conjugation.from_table(table))
            shelf[key] = conjugations
        return shelf[key]


def find_conjugation(infinitive: str, force: bool, fail_if_missing: bool = True) -> Optional[Conjugation]:
    conjugations = read_conjugations(force)
    cs = [c for c in conjugations if sanitize_text(c.infinitive) == sanitize_text(infinitive)]
    if len(cs) == 1:
        return cs[0]
    if fail_if_missing:
        raise ValueError(f"Missing conjugation for {infinitive}")
    if len(cs) == 0:
        return None
    raise ValueError(f"Multiple conjugations found for {infinitive}")


def verbs_matching_zaliznyak_class(short_class: str, stem_filter: Optional[str], force: bool):
    conjugations = read_conjugations(force)
    matching = [c for c in conjugations if c.verb_type.zaliznyak_class.short_class == short_class]
    if stem_filter is None:
        return matching

    reflexive_stem = stem_filter + "ся"
    matching_stem = [c for c in matching if
                     sanitize_text(c.infinitive).endswith(stem_filter) or sanitize_text(c.infinitive).endswith(
                         reflexive_stem)]
    return matching_stem


