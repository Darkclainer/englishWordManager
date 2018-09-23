import json
import aqt
from aqt.qt import (QWidget, QVBoxLayout, Qt)
from . import config
from .englishDictionary import Metaword
from .ankiinterface import AnkiInterface
from .metawordfinder import MetawordFinder
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditorholder import AnkiwordEditorHolder
from .ankiword import metawordToAnkiwordList
from .ankiwordwidget import AnkiwordWidget

def loadTestMetaword():
    with open('/home/dio/.local/share/Anki2/addons21/englishWordManager/testmetaword.json') as f:
        metawordJson = json.load(f)

    return Metaword.fromSON(metawordJson)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ankiInterface = AnkiInterface(config.config['modelName'])

        self.setMinimumSize(500, 700)
        self.setupUI()

        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordFinder = MetawordFinder()
        vbox.addWidget(self.metawordFinder)

        self.metawordFinder.newMetaword.connect(self.setMetaword)

        #ankiwordEditor = AnkiwordEditorHolder(ankiInterface=self.ankiInterface, parent=self)
        #vbox.addWidget(ankiwordEditor)
        #self.ankiwordEdit = ankiwordEditor
        #self.ankiwordView.getEditor = lambda: self.ankiwordEdit

        self.ankiwordWidget = AnkiwordWidget(ankiInterface=self.ankiInterface)
        vbox.addWidget(self.ankiwordWidget)
        self.setMetaword(loadTestMetaword())

        self.show()

    def setMetaword(self, metaword):
        ankiwords = metawordToAnkiwordList(metaword)

        # now find words from anki database and add it to list
        letterings = {ankiword.lettering for ankiword in ankiwords}
        for lettering in letterings:
            ankiwords.extend(self.ankiInterface.findAnkiwords(lettering))

        self.ankiwordWidget.resetAnkiwordList(ankiwords)

