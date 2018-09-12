"""This module define Ankiword class and metawordToAnkiwordList function"""
from .ankiinterface import config

class Ankiword:
    """Class used to bound Word with Anki"""
    def __init__(self, lettering, *, language):
        self.lettering = lettering
        self.language = language

        self.partOfSpeech = ''
        self.transcriptions = []
        self.definition = ''
        self. examples = []
        self.hint = ''
        self.variant = ''

        # note id (nid) in anki database
        self.noteId = None

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

    @staticmethod
    def fromNote(note):
        """Construct Ankiword from Note (from anki database). That function also sets noteId"""
        def getFromNote(fieldName):
            return note[config[fieldName]]

        ankiword = Ankiword(getFromNote('lettering'), language=getFromNote('language'))
        ankiword.partOfSpeech = getFromNote('partOfSpeech')
        ankiword.transcriptions = ('anki', getFromNote('transcription'))
        ankiword.definition = getFromNote('definition')
        ankiword.examples = [getFromNote('context'), getFromNote('example')]
        ankiword.hint = getFromNote('hint')
        ankiword.variant = getFromNote('variant')
        ankiword.noteId = note.id
        return ankiword

def metawordToAnkiwordList(metaword):
    """Convert Metaword to list of Ankiwords"""
    ankiwordList = []
    for word in metaword:
        for definition in word.definitions:
            ankiwordList.append(Ankiword.fromWord(word, definition))

    return ankiwordList
