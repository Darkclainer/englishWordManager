"""This module defines the main window of widget."""
import aqt
from aqt.qt import (QWidget, QVBoxLayout, Qt)
from .metawordfinder import MetawordFinder
from .ankiword import metawordToAnkiwordList
from .ankiwordlistwidget import AnkiwordListWidget

class MainWindow(QWidget):
    """The main window of widget, which includes input widget and list of ankiwords."""

    def __init__(self, *, ankiInterface, **kargs):
        super().__init__(**kargs)

        self.ankiInterface = ankiInterface

        self.setMinimumSize(500, 700)
        self._setupUI()

        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def _setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordFinder = MetawordFinder()
        vbox.addWidget(self.metawordFinder)
        self.metawordFinder.newMetaword.connect(self.setMetaword)

        self.ankiwordListWidget = AnkiwordListWidget(ankiInterface=self.ankiInterface)
        vbox.addWidget(self.ankiwordListWidget)

        self.show()

    def setMetaword(self, metaword):
        """Break of metaword to ankiwords and add local ankiword to widget."""
        ankiwords = metawordToAnkiwordList(metaword)

        # now find words from anki database and add it to list
        letterings = {ankiword.lettering for ankiword in ankiwords}
        for lettering in letterings:
            ankiwords.extend(self.ankiInterface.findAnkiwords(lettering))

        self.ankiwordListWidget.resetAnkiwordList(ankiwords)

    def closeEvent(self, event):
        """Overrided. Update aqt interface."""
        aqt.mw.reset()
        super().closeEvent(event)
