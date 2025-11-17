from utils.types import checked_type


# There exist verbs (e.g. посыпать), with the same infinitive, yet
# existing in both aspects - hence we add aspect to the identifier
class VerbIdentifier:
    def __init__(self, infinitive: str, aspect: str):
        self.infinitive: str = checked_type(infinitive, str)
        self.aspect: str = checked_type(aspect, str)