from . import ankiword
from . import ankiwordeditor
from . import metawordfinder
from . import ankiwordmodel
from . import htmldelegate
from . import movablelist
from . import ankiwordview
from . import treehtmlview
from . import exampleswidget
from . import transcriptionwidget

import importlib
importlib.reload(ankiword)
importlib.reload(metawordfinder)
importlib.reload(htmldelegate)
importlib.reload(treehtmlview)
importlib.reload(movablelist)
importlib.reload(ankiwordmodel)
importlib.reload(ankiwordview)
importlib.reload(exampleswidget)
importlib.reload(transcriptionwidget)
importlib.reload(ankiwordeditor)

import json #test purpose
import aqt
from aqt.qt import (QApplication, QWidget, QVBoxLayout)
from .englishDictionary import Metaword

from .ankiword import metawordToAnkiwordList
from .metawordfinder import MetawordFinder
from .ankiwordview import AnkiwordView
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditor import AnkiwordEditor

import traceback

#plugins module for reload

def loadTestMetaword():
    with open('/home/dio/.local/share/Anki2/addons21/metawordGui/testmetaword.json') as f:
        metawordJson = json.load(f)

    return Metaword.fromSON(metawordJson)

class MetawordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(500, 700)
        self.setupUI()

    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordFinder = MetawordFinder()
        vbox.addWidget(self.metawordFinder)

        self.ankiwordView = AnkiwordView()
        vbox.addWidget(self.ankiwordView)

        self.ankiwordModel = AnkiwordModel()
        self.ankiwordView.setModel(self.ankiwordModel)
        self.setMetaword(loadTestMetaword())

        self.metawordFinder.newMetaword.connect(self.setMetaword)

        ankiwordEditor = AnkiwordEditor(self)
        vbox.addWidget(ankiwordEditor)
        self.ankiwordEdit = ankiwordEditor
        self.ankiwordView.getEditor = lambda: self.ankiwordEdit

        self.show()


    def setMetaword(self, metaword):
        ankiwordList = metawordToAnkiwordList(metaword)
        self.ankiwordModel.setAnkiwordList(ankiwordList)
        self.ankiwordView.expandAll()


aqt.mw.metawordWindow = MetawordWindow()
