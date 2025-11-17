from more_itertools import flatten

from grammar.conjugation import Conjugation
from utils.utils import group_into_dict
from wikipedia.verb.verb_identifier import VerbIdentifier
from wikipedia.verb.verb_definition import VerbDefinition
from utils.types import checked_type, checked_list_type


class WikipediaVerbInfo:
    def __init__(
            self,
            identifier: VerbIdentifier,
            correspondents: list[str],
            conjugation: Conjugation,
            definitions: list[VerbDefinition],
            derived_terms: list[str],
            related_terms: list[str]):
        assert len(definitions) > 0, f"No definitions for verb {identifier.infinitive}"
        self.identifier: VerbIdentifier = checked_type(identifier, VerbIdentifier)
        self.correspondents: list[str] = checked_list_type(correspondents, str)
        self.conjugation: Conjugation = checked_type(conjugation, Conjugation)
        self.definitions: list[VerbDefinition] = checked_list_type(definitions, VerbDefinition)
        self.derived_terms: list[str] = checked_list_type(derived_terms, str)
        self.related_terms: list[str] = checked_list_type(related_terms, str)

    @staticmethod
    def merge(verbs: list['WikipediaVerbInfo']) -> 'list[WikipediaVerbInfo]':
        grouped = group_into_dict(verbs, lambda verb: (verb.identifier, verb.conjugation))
        merged = []
        for (id, conj), group in grouped.items():
            merged_correspondents = list(set(flatten([v.correspondents for v in group])))
            merged_definitions = list(flatten([v.definitions for v in group]))
            merged_derived_terms = list(flatten([v.derived_terms for v in group]))
            merged_related_terms = list(flatten([v.related_terms for v in group]))
            merged.append(
                WikipediaVerbInfo(
                    id,
                    merged_correspondents,
                    conj,
                    merged_definitions,
                    merged_derived_terms,
                    merged_related_terms
                )
            )

        return merged
