import csv
from pathlib import Path
from typing import List


def write_csv_file(path, table):
    with open(path, 'wt', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(table)


def read_csv_file(path: Path) -> List[List[str]]:
    with open(path, 'rt', newline='') as f:
        return list(row for row in csv.reader(f))
