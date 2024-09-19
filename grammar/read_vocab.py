import shelve
from pathlib import Path

from utils.csv_utils import read_csv_file
from utils.types import checked_type, checked_list_type

VOCAB_CSV_PATH = Path(__file__).parent.parent / 'resources' / '10 000 Russian words.csv'
SHELF_PATH = Path(__file__).parent / "_vocab_10000.shelf"

class VocabItem:
    def __init__(self, index: int, russian: str, english: str, notes: str):
        self.index: int = checked_type(index, int)
        self.russian: str = checked_type(russian, str)
        self.english: str = checked_type(english, str)
        self.notes: str = checked_type(notes, str)

class Vocab:
    def __init__(self, items: list[VocabItem]):
        self.items: list[VocabItem] = checked_list_type(items, VocabItem)


def read_vocab_10000(force: bool) -> Vocab:
    key = "Vocab"
    with shelve.open(str(SHELF_PATH)) as shelf:
        if key not in shelf or force:
            table = read_csv_file(VOCAB_CSV_PATH)
            items = []
            for i, row in enumerate(table):
                russian, english = row[:2]
                if len(row) >= 3:
                    notes = row[2].replace("|", "<br>")
                else:
                    notes = ""
                items.append(VocabItem(i, russian, english, notes))
            shelf[key] = Vocab(items)
        return shelf[key]