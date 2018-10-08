"""This module define class AnkiInterface used for interacting with anki database."""
import anki
from aqt import mw
from .ankiword import Ankiword

class NoModel(Exception):
    """If in anki databases currently no appropriate model."""
    pass
class AlreadySaved(Exception):
    """If someone tries save same word twice."""
    pass

class AnkiInterface:
    """Class used for interacting with anki database."""

    def __init__(self, config):
        # We need check is there such model and have it necessary fields
        self.config = config
        self._checkModel(config['modelName'])

        self.model = mw.col.models.byName(config['modelName'])

    def _findNotes(self, fieldName, fieldValue):
        notes = mw.col.db.execute('select id, flds from notes where mid = ? and flds like ?',
                                  self.model['id'], '%{0}%'.format(fieldValue))
        fieldIndex = self._getFieldIndex(fieldName)
        return [nid for nid, flds in notes
                if anki.utils.splitFields(flds)[fieldIndex] == fieldValue]

    def findAnkiwords(self, lettering):
        """Return anki Note with field config['fields']['lettering'] equal to lettering."""
        noteIds = self._findNotes('lettering', lettering)
        return [Ankiword.fromNote(mw.col.getNote(nid), self.config) for nid in noteIds]

    def _getFieldIndex(self, fieldName):
        fieldModelName = self.config['fields'][fieldName]
        return next(field['ord'] for field in self.model['flds'] if field['name'] == fieldModelName)

    def _saveAnkiwordToNote(self, ankiword, note):
        fields = self.config['fields']
        def saveToNote(fieldName, data):
            note[fields[fieldName]] = data

        saveToNote('lettering', ankiword.lettering)
        saveToNote('hint', ankiword.hint)
        saveToNote('partOfSpeech', ankiword.partOfSpeech)
        saveToNote('definition', ankiword.definition)

        numberOfExamples = len(ankiword.examples)
        if numberOfExamples > 0:
            saveToNote('context', ankiword.examples[0])
        if numberOfExamples > 1:
            saveToNote('example', ankiword.examples[1])

        if ankiword.transcriptions:
            saveToNote('transcription', ankiword.transcriptions[0][1])

        saveToNote('language', ankiword.language)

    def saveAnkiword(self, ankiword):
        """Add new note in anki db or update existing with information in ankiword.

        If the ankiword have noteId attribute - the ankiword will be updated,
        else new note will be added to bd and it's id will be saved in noteId attribute.
        """
        model = None if ankiword.noteId else self.model
        note = anki.notes.Note(mw.col, model, ankiword.noteId)

        for nid in self._findNotes('definition', ankiword.definition):
            if nid != ankiword.noteId:
                raise AlreadySaved()

        self._saveAnkiwordToNote(ankiword, note)

        if not ankiword.noteId:
            mw.col.addNote(note)
        else:
            note.flush()

        ankiword.noteId = note.id

    @staticmethod
    def removeAnkiword(ankiword):
        """If the ankiword have noteId attribute - remove note with this id.

        ankiword.noteId will be None after calling this function.
        """
        if ankiword.noteId:
            mw.col.remNotes([ankiword.noteId])
            ankiword.noteId = None

    def _checkModel(self, modelName):
        model = mw.col.models.byName(modelName)
        if not model:
            raise NoModel('Not found model: "{0}".'.format(modelName))

        self._checkModelFields(model)

    def _checkModelFields(self, model):
        modelFieldNames = mw.col.models.fieldNames(model)
        mustBeFieldNames = self.config['fields'].values()
        for fieldName in mustBeFieldNames:
            if not fieldName in modelFieldNames:
                raise NoModel('In model must be field: "{0}".'.format(fieldName))
