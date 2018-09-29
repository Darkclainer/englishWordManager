import json
import aqt
from aqt.qt import (QWidget, QVBoxLayout, Qt)
from .englishDictionary import Metaword
from .metawordfinder import MetawordFinder
from .ankiword import metawordToAnkiwordList
from .ankiwordwidget import AnkiwordWidget

class MainWindow(QWidget):
    def __init__(self, *, ankiInterface, **kargs):
        super().__init__(**kargs)

        self.ankiInterface = ankiInterface

        self.setMinimumSize(500, 700)
        self.setupUI()

        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordFinder = MetawordFinder()
        vbox.addWidget(self.metawordFinder)

        self.metawordFinder.newMetaword.connect(self.setMetaword)

        self.ankiwordWidget = AnkiwordWidget(ankiInterface=self.ankiInterface)
        vbox.addWidget(self.ankiwordWidget)

        self.show()

    def setMetaword(self, metaword):
        ankiwords = metawordToAnkiwordList(metaword)

        # now find words from anki database and add it to list
        letterings = {ankiword.lettering for ankiword in ankiwords}
        for lettering in letterings:
            ankiwords.extend(self.ankiInterface.findAnkiwords(lettering))

        self.ankiwordWidget.resetAnkiwordList(ankiwords)
        
    def closeEvent(self, event):
        aqt.mw.reset()
        super().closeEvent(event)
