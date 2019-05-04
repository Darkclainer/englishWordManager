"""This module define widget for obtaining lemma list through web dictionary"""
import sys
import traceback

import requests
import aqt
from aqt.qt import (pyqtSignal, QThread, QLineEdit,
                    QRegExp, QRegExpValidator, QCompleter)

from .camdict import query
from .camdict.exceptions import QueryException

HTTP_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'
}

class LemmasRequester(QThread):
    """Auxiliary class for receiving lemmas in seperated thread"""
    lemmasReceived = pyqtSignal(list)
    suggestionsReceived = pyqtSignal(list)
    exceptionReceived = pyqtSignal()

    def __init__(self, lemma_query, query_kargs):
        QThread.__init__(self)
        self.lemma_query = lemma_query
        self.query_kargs = query_kargs

    def run(self):
        """
        If lemma list correctly received then emit lemmasReceived
        If suggestions received then emit suggestionsReceived
        if exception Exception raised then emit exceptionReceived
        """
        try:
            responce_type, responce = query.query(str(self.lemma_query), **self.query_kargs)
            #aqt.utils.showInfo('responce_type "{}"; responce "{}"'.format(responce_type, responce))
            #aqt.utils.showInfo('{}'.format(str(self.lemma_query)))
            if responce_type == 'word_id':
                lemmas = query.query_lemma(responce, **self.query_kargs)
                self.lemmasReceived.emit(lemmas)
            else:
                suggestions = query.query_suggestions(responce, **self.query_kargs)
                self.suggestionsReceived.emit(suggestions)
        except Exception as exception:
            sys.stderr.write(traceback.format_exc())
            self.exceptionReceived.emit()

class LemmaLineEdit(QLineEdit):
    """QLineEdit widget that automatically find lemmas based on entered information.
    If suggestion was received then it lists suggestions.
    It changes color depending on its state.
    """
    newLemmas = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        lemmaRegExp = QRegExp('[A-Za-z]+([ -]([A-Za-z]+))* ?')
        validator = QRegExpValidator(lemmaRegExp)
        self.setValidator(validator)

        self.returnPressed.connect(self.returnPressedSlot)

        self.textEdited.connect(self.textEditedSlot)

        self.lemmasRequester = None

        self.defaultCompleter = QCompleter()
        self.setCompleter(self.defaultCompleter)

        self.setLookEditing()

        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)

    def setLookSearching(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid brown')
    def setLookEditing(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid blue')
    def setLookBad(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid red')
    def setLookOk(self):
        """Change appereance of widget, but not more"""
        self.setStyleSheet('border: 1px solid green')

    def textEditedSlot(self, text):
        """Called when text changed."""
        self.setLookEditing()
        self._dropLemmasRequester()
        self._dropCompleter()

    def _dropLemmasRequester(self):
        requester = self.lemmasRequester
        if requester:
            requester.exit()
            requester.lemmasReceived.disconnect(self.lemmasReceived)
            requester.suggestionsReceived.disconnect(self.suggestionsReceived)
            requester.exceptionReceived.disconnect(self.exceptionReceived)
            self.lemmasRequester = None

    def _dropCompleter(self):
        if self.completer():
            self.completer().popup().close()
            self.setCompleter(None)

    def returnPressedSlot(self):
        """Called when enter was pressed"""
        self.setLookSearching()
        self.startSearching()

    def lemmasReceived(self, lemmas):
        """Called when Metaword received from the web"""
        self.setLookOk()
        self.newLemmas.emit(lemmas)

    def completerActivated(self, query):
        """Called when user click on item in completer list"""
        self.returnPressedSlot()

    def suggestionsReceived(self, suggestions):
        """Called when Suggestion recieved."""
        self.setLookBad()
        completer = QCompleter(suggestions)
        self.setCompleter(completer)

        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        completer.activated.connect(self.completerActivated)
        completer.complete()

    def exceptionReceived(self):
        """Callled when exception received, not Metaword"""
        self.setLookBad()

    def startSearching(self):
        """Start searching Metaword based on current text content of widget"""
        requester = LemmasRequester(self.text(), dict(session=self.session))

        requester.lemmasReceived.connect(self.lemmasReceived)
        requester.suggestionsReceived.connect(self.suggestionsReceived)
        requester.exceptionReceived.connect(self.exceptionReceived)

        requester.start()

        self.lemmasRequester = requester
