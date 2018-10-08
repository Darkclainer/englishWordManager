"""This module defines function 'start' that is called on triggering action in anki menu."""
import aqt
from .config import getConfig, setConfig
from . import templates
from .ankiinterface import AnkiInterface, NoModel
from .mainwindow import MainWindow

def start():
    """Get config, AnkiInterface and create MainWindow."""
    config = getConfig()
    ankiInterface = getAnkiInterface(config)
    if not ankiInterface:
        return

    aqt.mw.englishWordManagerWindow = MainWindow(ankiInterface=ankiInterface)

def getAnkiInterface(config):
    """Get ankiInterface based on current config.

    It can changes config while interacting with user
    """

    # Loop.
    # 1. If model with modelName suits our purpose go to 2, else 3
    # 2. return AnkiInterface(modelName)
    # 3. Ask user three options: Enter another name, create default model, cancel
    # 4. Another name: ask user new name and go to 1 (change config)
    # 5. Create default model: create new default model and return it

    isNameChanged = False
    while True:
        try:
            ankiInterface = AnkiInterface(config)
            # all ok - we can save new name
            if isNameChanged:
                aqt.utils.showInfo('newConfig')
                setConfig(config)
            return ankiInterface

        except NoModel as exception:
            msgReason = 'Can not find suitable model with model name: \
"{0}", because:\n{1}'.format(config['modelName'], exception)
            newModelName = _getNewModelName(config, msgReason)
            if not newModelName:
                return None

            isNameChanged = (newModelName != config['modelName'] or isNameChanged)
            config['modelName'] = newModelName

def _getNewModelName(config, msgReason):
    """Prompt user how he/she want to deal with defining new model name."""

    prompt = msgReason + '''\n\nYou can:
    a) Create new default model
    b) Enter another model name
    c) Cancle'''
    buttons = ['c) Cancel', 'b) Change name', 'a) Create']
    # get first character from answer (a,b,c)
    answer = aqt.utils.askUserDialog(prompt, buttons).run()[0]

    if answer in 'ab':
        modelName = aqt.utils.getOnlyText('Enter new model name:')
        if not modelName:
            return None

    if answer == 'a':
        return _createNewModel(config, modelName)
    if answer == 'b':
        return modelName
    # Cancel
    return None

def _addTemplate(config, model, name, question, answer):
    template = aqt.mw.col.models.newTemplate(name)
    template['qfmt'] = question % config['fields']
    template['afmt'] = answer % config['fields']

    template['did'] = aqt.mw.col.decks.id(config['deck'])

    aqt.mw.col.models.addTemplate(model, template)

def _addTemplates(config, model):
    for template in templates.CARD_TEMPLATES:
        _addTemplate(config, model, **template)

def _createNewModel(config, modelName):
    models = aqt.mw.col.models
    # modelName must be unique
    model = models.new(modelName)
    model['css'] = templates.CSS
    models.add(model)

    # add all required fileds in correct order
    fieldNames = config['fields']
    fieldOrds = config['fieldsOrd']
    for originalFieldName in fieldOrds:
        fieldName = fieldNames[originalFieldName]
        newField = models.newField(fieldName)
        models.addField(model, newField)

    # set lettering as sort index
    fieldMap = models.fieldMap(model)
    idx = fieldMap[fieldNames['lettering']][0]
    models.setSortIdx(model, idx)

    # add templates
    _addTemplates(config, model)
    return model['name']
