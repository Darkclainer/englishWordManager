"""This module define Ankiword class and metawordToAnkiwordList function"""
import copy

class Ankiword:
    """Class used to bound Word with Anki"""
    def __init__(self, lettering, *, language):
        self.lettering = lettering
        self.language = language

        self.partOfSpeech = None
        self.transcriptions = []
        self.definition = ''
        self. examples = []
        self.hint = ''
        self.variant = ''

    @staticmethod
    def fromWord(word, definition):
        """Construct Ankiword from some word and definition"""
        ankiword = Ankiword(word.lettering, language=word.language)
        ankiword.partOfSpeech = word.partOfSpeech
        ankiword.transcriptions = list(word.transcriptions.items())

        ankiword.definition = definition.text
        ankiword.examples = list(definition.examples)
        ankiword.hint = definition.hint
        ankiword.variant = definition.variant
       # ankiword.definition = copy.deepcopy(definition)
        return ankiword

def metawordToAnkiwordList(metaword):
    """Convert Metaword to list of Ankiwords"""
    ankiwordList = []
    for word in metaword:
        for definition in word.definitions:
            ankiwordList.append(Ankiword.fromWord(word, definition))

    return ankiwordList
