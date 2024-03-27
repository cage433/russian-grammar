from typing import List

from grammar.conjugation import Conjugation


class ConjugationCSV:
    @staticmethod
    def from_conjugation_to_csv(conjugation: Conjugation) -> List[List[str]]:
        table = [
            ["Infinitive", conjugation.infinitive],
            ["Category", conjugation.verb_type.zaliznyak_class.category],
            ["StressRule", conjugation.verb_type.zaliznyak_class.category],
            ["Verb Type", conjugation.verb_type],
            ["Aspect", conjugation.aspect],
            ["Category", conjugation.category],
            ["Present", conjugation.present],
            ["Past", conjugation.past],
            ["Future", conjugation.future],
            ["Imperative", conjugation.imperative],
            ["Present Participle", conjugation.present_participle],
            ["Past Participle", conjugation.past_participle]

        ]
