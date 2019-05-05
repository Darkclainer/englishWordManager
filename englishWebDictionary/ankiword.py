"""This module define Ankiword class"""

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
    def fromLemma(lemma):
        """Construct Ankiword from some word and definition"""
        ankiword = Ankiword(lemma.lemma, language=lemma.language)
        ankiword.partOfSpeech = lemma.part_of_speech
        ankiword.transcriptions = list(lemma.transcriptions.items())

        ankiword.definition = lemma.definition
        ankiword.examples = list(lemma.examples)
        ankiword.hint = lemma.guide_word
        # if we have variant - set this lettering for word
        if lemma.alternative_form:
            ankiword.lettering = lemma.alternative_form

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
