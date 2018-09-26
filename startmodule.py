"""This module define function start that called on triggering action in anki menu"""
import aqt
from .config import getConfig, setConfig
from .ankiinterface import AnkiInterface, NoModel
from .mainwindow import MainWindow

def start():
    config = getConfig()
    ankiInterface = getAnkiInterface(config)
    if not ankiInterface:
        return
    aqt.mw.englishWordManagerWindow = MainWindow(ankiInterface=ankiInterface)

def getAnkiInterface(config):
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
            newModelName = getNewModelName(config, msgReason)
            if not newModelName:
                return

            isNameChanged = (newModelName != config['modelName'] or isNameChanged)
            config['modelName'] = newModelName

def getNewModelName(config, msgReason):
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
        return createNewModel(config, modelName)
    elif answer == 'b':
        return modelName
    else: # Cancel
        return None

def createNewModel(config, modelName):
    # modelName must be unique
    model = aqt.mw.col.models.new(modelName)
    aqt.mw.col.models.add(model)

    fieldNames = config['fields'].values()
    for fieldName in fieldNames:
        newField = aqt.mw.col.models.newField(fieldName)
        aqt.mw.col.models.addField(model, newField)

    return model['name']

    # add template
    
