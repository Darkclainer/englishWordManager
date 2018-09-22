import json
from aqt.qt import (QWidget, QVBoxLayout)
from . import config
from .englishDictionary import Metaword
from .ankiinterface import AnkiInterface
from .metawordfinder import MetawordFinder
from .ankiwordview import AnkiwordView
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditorholder import AnkiwordEditorHolder
from .ankiword import metawordToAnkiwordList

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


    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordFinder = MetawordFinder()
        vbox.addWidget(self.metawordFinder)

        self.ankiwordView = AnkiwordView()
        vbox.addWidget(self.ankiwordView)

        self.ankiwordModel = AnkiwordModel(ankiInterface=self.ankiInterface)
        self.ankiwordView.setModel(self.ankiwordModel)
        self.setMetaword(loadTestMetaword())

        self.metawordFinder.newMetaword.connect(self.setMetaword)

        ankiwordEditor = AnkiwordEditorHolder(ankiInterface=self.ankiInterface, parent=self)
        vbox.addWidget(ankiwordEditor)
        self.ankiwordEdit = ankiwordEditor
        self.ankiwordView.getEditor = lambda: self.ankiwordEdit

        self.show()


    def setMetaword(self, metaword):
        ankiwords = metawordToAnkiwordList(metaword)

        # now find words from anki database and add it to list
        letterings = {ankiword.lettering for ankiword in ankiwords}
        for lettering in letterings:
            ankiwords.extend(self.ankiInterface.findAnkiwords(lettering))

        self.ankiwordModel.setAnkiwordList(ankiwords)

        self.ankiwordView.expandAll()
