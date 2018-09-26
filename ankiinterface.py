import anki
from aqt import mw
from .ankiword import Ankiword


class NoModel(Exception):
    pass
class AlreadySaved(Exception):
    pass

class AnkiInterface:
    def __init__(self, config):
        # We need check is there such model and have it necessary fields
        self.config = config
        self._checkModel(config['modelName'])

        self.model = mw.col.models.byName(config['modelName'])

    def _findNotes(self, fieldName, fieldValue):
        notes = mw.col.db.execute('select id, flds from notes where mid = ? and flds like ?', 
                                  self.model['id'], '%{0}%'.format(fieldValue))
        fieldIndex = self._getFieldIndex(fieldName)
        founded = []
        return [nid for nid, flds in notes 
                if anki.utils.splitFields(flds)[fieldIndex] == fieldValue]

    def findAnkiwords(self, lettering):
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

    def _checkModel(self, modelName):
        model = mw.col.models.byName(modelName)
        if not model:
            raise NoModel('Not found model: "{0}".'.format(modelName))

        self._checkModelFields(model)

    def _checkModelFields(self, model):
        modelFieldNames = mw.col.models.fieldNames(model)
        mustBeFieldNames = self.config['fields'].values()
        #aqt.utils.showInfo('Models: {0}\nMustBe: {1}'.format(modelFieldNames, mustBeFieldNames))
        for fieldName in mustBeFieldNames:
            if not fieldName in modelFieldNames:
                raise NoModel('In model must be field: "{0}".'.format(fieldName))
