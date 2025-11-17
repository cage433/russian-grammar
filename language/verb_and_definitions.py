from grammar.conjugation import Conjugation
from language.verb.verb_info import VerbDefinition
from utils.types import checked_type, checked_list_type


class VerbAndDefinitions:
    def __init__(
            self,
            infinitive: str,
            aspect: str,
            correspondents: list[str],
            conjugation: Conjugation,
            definitions: list[VerbDefinition],
            derivedTerms: list[str],
            relatedTerms: list[str]):
        self.infinitive: str = checked_type(infinitive, str)
        self.aspect: str = checked_type(aspect, str)
        self.correspondents: list[str] = checked_list_type(correspondents, str)
        self.conjugation: Conjugation = checked_type(conjugation, Conjugation)
        self.definitions: list[VerbDefinition] = checked_list_type(definitions, VerbDefinition)
        self.derivedTerms: list[str] = checked_list_type(derivedTerms, str)
        self.relatedTerms: list[str] = checked_list_type(relatedTerms, str)
