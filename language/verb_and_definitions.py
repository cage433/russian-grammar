from typing import Optional

from grammar.conjugation import Conjugation
from scraper.verb_parser import VerbDefinitionAndExamples, VerbRelatedTerms, VerbDerivedTerms
from utils.types import checked_type, checked_optional_type


class VerbAndDefinitions:
    def __init__(
            self,
            conjugation: Conjugation,
            definitions: VerbDefinitionAndExamples,
            derivedTerms: Optional[VerbDerivedTerms],
            relatedTerms: Optional[VerbRelatedTerms]):
        self.conjugation: Conjugation = checked_type(conjugation, Conjugation)
        self.definitions: VerbDefinitionAndExamples = checked_type(definitions, VerbDefinitionAndExamples)
        self.derivedTerms: Optional[VerbDerivedTerms] = checked_optional_type(derivedTerms, VerbDerivedTerms)
        self.relatedTerms: Optional[VerbRelatedTerms] = checked_optional_type(relatedTerms, VerbRelatedTerms)
