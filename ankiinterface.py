import anki
from aqt import mw
from .config import config
from .ankiword import Ankiword


def createNewModel(modelName):
    # modelName must be unique
    model = mw.col.models.new(modelName)
    mw.col.models.add(model)

    fieldNames = config['fields'].values()
    for fieldName in fieldNames:
        newField = mw.col.models.newField(fieldName)
        mw.col.models.addField(model, newField)

class NoModel(Exception):
    pass
class AlreadySaved(Exception):
    pass

class AnkiInterface:
    def __init__(self, modelName):
        # We need check is there such model and have it necessary fields
        self._checkModel(modelName)

        self.model = mw.col.models.byName(modelName)

    def _findNotes(self, fieldName, fieldValue):
        notes = mw.col.db.execute('select id, flds from notes where mid = ? and flds like ?', 
                                  self.model['id'], '%{0}%'.format(fieldValue))
        fieldIndex = self._getFieldIndex(fieldName)
        founded = []
        return [nid for nid, flds in notes 
                if anki.utils.splitFields(flds)[fieldIndex] == fieldValue]

    def findAnkiwords(self, lettering):
        noteIds = self._findNotes('lettering', lettering)
        return [Ankiword.fromNote(mw.col.getNote(nid)) for nid in noteIds]

    def _getFieldIndex(self, fieldName):
        fieldModelName = config['fields'][fieldName]
        return next(field['ord'] for field in self.model['flds'] if field['name'] == fieldModelName)

    @staticmethod
    def _saveAnkiwordToNote(ankiword, note):
        fields = config['fields']
        def saveToNote(fieldName, data):
            note[fields[fieldName]] = data

        saveToNote('lettering', ankiword.lettering)
        saveToNote('hint', ankiword.hint)
        saveToNote('partOfSpeech', ankiword.partOfSpeech)
        saveToNote('definition', ankiword.definition)

        if len(ankiword.examples) > 0:
            saveToNote('context', ankiword.examples[0])
        if len(ankiword.examples) > 1:
            saveToNote('example', ankiword.examples[1])

        if len(ankiword.transcriptions) > 0:
            saveToNote('transcription', ankiword.transcriptions[0][1])

    def saveAnkiword(self, ankiword):
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

    def removeAnkiword(self, ankiword):
        if ankiword.noteId:
            mw.col.remNotes([ankiword.noteId])

    @staticmethod
    def _checkModel(modelName):
        model = mw.col.models.byName(modelName)
        if not model:
            raise NoModel('Not found model: "{0}".'.format(modelName))

        AnkiInterface._checkModelFields(model)

    @staticmethod
    def _checkModelFields(model):
        modelFieldNames = mw.col.models.fieldNames(model)
        mustBeFieldNames = config['fields'].values()
        #aqt.utils.showInfo('Models: {0}\nMustBe: {1}'.format(modelFieldNames, mustBeFieldNames))
        for fieldName in mustBeFieldNames:
            if not fieldName in modelFieldNames:
                raise NoModel('In model must be field: "{0}".'.format(fieldName))
