import unicodedata
from typing import Iterable, Callable, Dict, List, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def sanitize_text(word):
    return ''.join(filter(
        lambda x: unicodedata.category(x) != 'Mn' and x not in ['△', '*'],
        unicodedata.normalize('NFD', word)
    ))


def strip_stress_marks(text: str) -> str:
    b = text.encode('utf-8')
    # correct error where latin accented ó is used
    b = b.replace(b'\xc3\xb3', b'\xd0\xbe')
    # correct error where latin accented á is used
    b = b.replace(b'\xc3\xa1', b'\xd0\xb0')
    # correct error where latin accented é is used
    b = b.replace(b'\xc3\xa0', b'\xd0\xb5')
    # correct error where latin accented ý is used
    b = b.replace(b'\xc3\xbd', b'\xd1\x83')
    # remove combining diacritical mark
    b = b.replace(b'\xcc\x81',b'').decode()
    return b

def group_into_dict(iterable: Iterable[T], key_constructor: Callable[[T], R]) -> Dict[R, List[T]]:
    """Builds a dict whose values are disjoint sub-lists of `iterable`, which share the same `property` value, the
    latter being the associated key.

    The sub-lists constructed preserve order to the extent the original iterable does

    Equivalent to `groupBy` in the Scala collections library. Note that this is _not_ equivalent to `itertools.group_by`
    """
    result = {}
    for item in iterable:
        key = key_constructor(item)
        result[key] = result.get(key, []) + [item]

    return result
