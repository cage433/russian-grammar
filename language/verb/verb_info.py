from utils.types import checked_type, checked_list_type


class QuoteAndTranslation:
    def __init__(self, quote: str, translation: str):
        self.quote: str = checked_type(quote, str)
        self.translation: str = checked_type(translation, str)

    def __str__(self):
        return f"{self.quote} -- {self.translation}"

    def __repr__(self):
        return self.__str__()


class VerbDefinition:
    def __init__(self, meaning: str, quotes: list[QuoteAndTranslation]):
        self.meaning: str = checked_type(meaning, str)
        self.quotes: list[QuoteAndTranslation] = checked_list_type(quotes, QuoteAndTranslation)


class VerbDefinitionAndExamples:
    def __init__(self, infinitive: str, aspect: str, correspondents: list[str], definitions: list[VerbDefinition]):
        self.infinitive: str = checked_type(infinitive, str)
        self.aspect: str = checked_type(aspect, str)
        self.correspondents: list[str] = checked_list_type(correspondents, str)
        self.definitions: list[VerbDefinition] = checked_list_type(definitions, VerbDefinition)
