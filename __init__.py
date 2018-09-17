from . import config
from . import ankiword
from . import ankiwordeditor
from . import ankiwordeditorholder
from . import metawordfinder
from . import ankiwordmodel
from . import htmldelegate
from . import movablelist
from . import ankiwordview
from . import treehtmlview
from . import exampleswidget
from . import transcriptionwidget
from . import ankiinterface

import importlib
importlib.reload(config)
importlib.reload(ankiword)
importlib.reload(ankiinterface)
importlib.reload(metawordfinder)
importlib.reload(htmldelegate)
importlib.reload(treehtmlview)
importlib.reload(movablelist)
importlib.reload(ankiwordmodel)
importlib.reload(ankiwordview)
importlib.reload(exampleswidget)
importlib.reload(transcriptionwidget)
importlib.reload(ankiwordeditor)
importlib.reload(ankiwordeditorholder)

import json #test purpose
import aqt
from aqt.qt import (QApplication, QWidget, QVBoxLayout)
from .englishDictionary import Metaword

from .ankiword import metawordToAnkiwordList
from .metawordfinder import MetawordFinder
from .ankiwordview import AnkiwordView
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditor import AnkiwordEditor
from .ankiwordeditorholder import AnkiwordEditorHolder
from .ankiinterface import AnkiInterface

import traceback

#plugins module for reload

def loadTestMetaword():
    with open('/home/dio/.local/share/Anki2/addons21/englishWordManager/testmetaword.json') as f:
        metawordJson = json.load(f)

    return Metaword.fromSON(metawordJson)

class MetawordWindow(QWidget):
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

        ankiwordEditor = AnkiwordEditorHolder(parent=self)
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


aqt.mw.metawordWindow = MetawordWindow()
