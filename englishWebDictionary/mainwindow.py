"""This module defines the main window of widget."""
import aqt
from aqt.qt import (QWidget, QVBoxLayout, Qt)
from .lemmalineedit import LemmaLineEdit
from .ankiword import Ankiword
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

        self.lemmaLineEdit = LemmaLineEdit()
        vbox.addWidget(self.lemmaLineEdit)
        self.lemmaLineEdit.newLemmas.connect(self.setLemmas)

        self.ankiwordListWidget = AnkiwordListWidget(ankiInterface=self.ankiInterface)
        vbox.addWidget(self.ankiwordListWidget)

        self.show()

    def setLemmas(self, lemmas):
        """Break of metaword to ankiwords and add local ankiword to widget."""
        ankiwords = [Ankiword.fromLemma(lemma) for lemma in lemmas]

        # now find words from anki database and add it to list
        letterings = {ankiword.lettering for ankiword in ankiwords}
        for lettering in letterings:
            ankiwords.extend(self.ankiInterface.findAnkiwords(lettering))

        self.ankiwordListWidget.resetAnkiwordList(ankiwords)

    def closeEvent(self, event):
        """Overrided. Update aqt interface."""
        aqt.mw.reset()
        super().closeEvent(event)
