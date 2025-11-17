from grammar.conjugation import Conjugation
from language.verb.verb_identifier import VerbIdentifier
from language.verb.verb_info import VerbDefinition
from utils.types import checked_type, checked_list_type


class WikipediaVerbInfo:
    def __init__(
            self,
            identifier: VerbIdentifier,
            correspondents: list[str],
            conjugation: Conjugation,
            definitions: list[VerbDefinition],
            derivedTerms: list[str],
            relatedTerms: list[str]):
        self.identifier: VerbIdentifier = checked_type(identifier, VerbIdentifier)
        self.correspondents: list[str] = checked_list_type(correspondents, str)
        self.conjugation: Conjugation = checked_type(conjugation, Conjugation)
        self.definitions: list[VerbDefinition] = checked_list_type(definitions, VerbDefinition)
        self.derivedTerms: list[str] = checked_list_type(derivedTerms, str)
        self.relatedTerms: list[str] = checked_list_type(relatedTerms, str)
