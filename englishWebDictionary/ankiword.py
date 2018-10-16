"""This module define Ankiword class and metawordToAnkiwordList function"""

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
        # if we have variant - set this lettering for word
        if definition.variant:
            ankiword.lettering = definition.variant

        return ankiword

    @staticmethod
    def fromNote(note, config):
        """Construct Ankiword from Note (from anki database). That function also sets noteId"""
        fields = config['fields']
        def getFromNote(fieldName):
            return note[fields[fieldName]]
        language = getFromNote('language') or config['preferredLanguage']
        ankiword = Ankiword(getFromNote('lettering'), language=language)
        ankiword.partOfSpeech = getFromNote('partOfSpeech')
        ankiword.transcriptions = [('anki', getFromNote('transcription'))]
        ankiword.definition = getFromNote('definition')
        ankiword.examples = [getFromNote('context'), getFromNote('example')]
        ankiword.hint = getFromNote('hint')
        ankiword.noteId = note.id
        return ankiword

def metawordToAnkiwordList(metaword):
    """Convert Metaword to list of Ankiwords"""
    ankiwordList = []
    for word in metaword:
        for definition in word.definitions:
            ankiwordList.append(Ankiword.fromWord(word, definition))

    return ankiwordList
