import aqt
from aqt import mw
import anki

config = mw.addonManager.getConfig('englishWordManager')

def createNewModel(modelName):
    # modelName must be unique
    model = mw.col.models.new(modelName)
    mw.col.models.add(model)

    fieldNames = config['fields'].values()
    for fieldName in fieldNames:
        newField = mw.col.models.newField(fieldName)
        mw.col.models.addField(model, newField)

class NoModel(Exception): pass

class AnkiInterface:
    def __init__(self, modelName):
        # We need check is there such model and have it necessary fields
        self._checkModel(modelName)

        self.model = mw.col.models.byName(modelName)

    def findNotes(self, lettering):
        notes = mw.col.db.execute('select id, flds from notes where mid = ? and flds like ?', self.model['id'], '%{0}%'.format(lettering))
        letteringIndex = self._getFieldIndex('lettering')
        founded = []
        for nid, flds in notes:
            fields = anki.utils.splitFields(flds)
            if fields[letteringIndex] == lettering:
                founded.append(mw.col.getNote(nid))
        return founded
            
    def _getFieldIndex(self, fieldName):
        fieldModelName = config['fields'][fieldName]
        return next(field['ord'] for field in self.model['flds'] if field['name'] == fieldModelName)

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

"""
mod = mw.col.models.byName('EnglishWord')
all =mw.col.db.all('select id, flds from notes where mid = ? and flds like ?', mod['id'], '%hike%')
for id, flds in all:
     print(anki.utils.splitFields(flds))
"""
