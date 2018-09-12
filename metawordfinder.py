"""This module define widget for obtaining Metaword through web dictionary"""
import sys
import traceback
from aqt.qt import (pyqtSignal, QThread, QLineEdit,
                    QRegExp, QRegExpValidator, QCompleter)
from .englishDictionary import Metaword, Suggestions, requestWord

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
}

class MetawordRequesterThread(QThread):
    """Auxiliary class for receiving Metaword in seperated thread"""
    metawordReceived = pyqtSignal(Metaword)
    suggestionsReceived = pyqtSignal(Suggestions)
    exceptionReceived = pyqtSignal(Exception)

    def __init__(self, getFunction):
        QThread.__init__(self)
        self.getFunction = getFunction

    def run(self):
        """Run getFunction in seperate thread.
        If metaword correctly received then emit metawordRecieved
        If exception Suggestion raised then emit suggestionsReceived
        if exception Exception raised then emit exceptionReceived
        """
        try:
            metaword = self.getFunction()
            self.metawordReceived.emit(metaword)
        except Suggestions as suggestions:
            self.suggestionsReceived.emit(suggestions)
        except Exception as exception:
            sys.stderr.write(traceback.format_exc())
            self.exceptionReceived.emit(exception)

class MetawordFinder(QLineEdit):
    """QLineEdit widget that automatically find metaword based on entered information.
    If suggestion was received then it lists suggestions.
    It changes color depend on its state.
    """
    newMetaword = pyqtSignal(Metaword)

    def __init__(self, parent=None):
        super().__init__(parent)

        metawordRegExp = QRegExp('[A-Za-z]+([ -]([A-Za-z]+))* ?')
        validator = QRegExpValidator(metawordRegExp)
        self.setValidator(validator)

        self.returnPressed.connect(self.returnPressedSlot)

        self.textEdited.connect(self.textEditedSlot)

        self.metawordRequesterThread = None

        self.defaultCompleter = QCompleter()
        self.setCompleter(self.defaultCompleter)

        self.setLookEdition()

    def setLookSearching(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid brown')
    def setLookEdition(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid blue')
    def setLookBad(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid red')
    def setLookOk(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid green')

    def textEditedSlot(self, text):
        """Called when text was edited."""
        self.setLookEdition()
        self._dropMetawordRequesterThread()
        self._dropCompleter()

    def _dropMetawordRequesterThread(self):
        requesterThread = self.metawordRequesterThread
        if requesterThread:
            requesterThread.exit()
            requesterThread.metawordReceived.disconnect(self.metawordReceived)
            requesterThread.suggestionsReceived.disconnect(self.suggestionsReceived)
            requesterThread.exceptionReceived.disconnect(self.exceptionReceived)
            self.metawordRequesterThread = None

    def _dropCompleter(self):
        if self.completer():
            self.completer().popup().close()
            self.setCompleter(None)

    def returnPressedSlot(self):
        """Called when enter was pressed"""
        self.setLookSearching()
        self.startSearching()

    def metawordReceived(self, metaword):
        """Called when Metaword received from the web"""
        self.setLookOk()
        self.newMetaword.emit(metaword)

    def completerActivated(self, query):
        """Called when user click on item in completer list"""
        self.returnPressedSlot()

    def suggestionsReceivesuggestionsReceived(self, suggestions):
        """Called when Suggestion recieved, not Metaword, from web"""
        self.setLookBad()
        completer = QCompleter(suggestions.suggestions)
        self.setCompleter(completer)

        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        completer.activated.connect(self.completerActivated)
        completer.complete()


    def exceptionReceived(self, exception):
        """Callled when exception received, not Metaword"""
        self.setLookBad()

    def startSearching(self):
        """Start searching Metaword based on current text content of widget"""
        thread = MetawordRequesterThread(
            lambda: requestWord(str(self.text()), headers=HTTP_HEADERS)
        )

        thread.metawordReceived.connect(self.metawordReceived)
        thread.suggestionsReceived.connect(self.suggestionsReceived)
        thread.exceptionReceived.connect(self.exceptionReceived)

        thread.start()

        self.metawordRequesterThread = thread
