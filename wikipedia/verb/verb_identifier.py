from scipy.optimize import anderson

from utils.types import checked_type


# There exist verbs (e.g. посыпать), with the same infinitive, yet
# existing in both aspects - hence we add aspect to the identifier
class VerbIdentifier:
    def __init__(self, infinitive: str, aspect: str):
        self.infinitive: str = checked_type(infinitive, str)
        self.aspect: str = checked_type(aspect, str)

    def __eq__(self, other):
        if not isinstance(other, VerbIdentifier):
            return False
        return (self.infinitive == other.infinitive
                and self.aspect == other.aspect)

    def __hash__(self):
        return hash((self.infinitive, self.aspect))