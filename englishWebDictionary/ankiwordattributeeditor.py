"""This module define AnkiwordAttributeEditor widget, that used for editing Ankiword."""
import copy
from aqt.qt import (QWidget, QGridLayout, QLabel, QTextEdit,
                    QLineEdit, Qt, QMargins)
from .exampleswidget import ExamplesWidget
from .transcriptionwidget import TranscriptionsWidget
#from .englishDictionary import Metaword, Suggestions

class AnkiwordAttributeEditor(QWidget):
    """Widget for actually editing ankiword (its attributes).

    Actually return shallow copy of previously setted ankiword with fields,
    changed accordingly to current widget state. This helps to preserve noteId and
    similar field.
    """

    def __init__(self, parent=None, preferredRegion='anki', **kargs):
        super().__init__(parent, **kargs)
        self._ankiword = None
        self._preferredRegion = preferredRegion
        self._setupUi()

    def _setupUi(self):
        layout = QGridLayout()
        # remove margins
        layout.setContentsMargins(QMargins())
        self.setLayout(layout)

        row = 0

        # 1st row
        label = QLabel(self, text='Lettering:')
        layout.addWidget(label, row, 0, alignment=Qt.AlignRight)

        widget = QLineEdit(self)
        layout.addWidget(widget, row, 1)
        label.setBuddy(widget)
        self.letteringEdit = widget
        row += 1

        # 2nd row
        label = QLabel(self, text='Hint:')
        layout.addWidget(label, row, 0, alignment=Qt.AlignRight)

        widget = QLineEdit(self)
        layout.addWidget(widget, row, 1)
        label.setBuddy(widget)
        self.hintEdit = widget
        row += 1

        # 3rd row
        label = QLabel(self, text='Part of speech:')
        layout.addWidget(label, row, 0, alignment=Qt.AlignRight)

        widget = QLineEdit(self)
        layout.addWidget(widget, row, 1)
        label.setBuddy(widget)
        self.partOfSpeechEdit = widget
        row += 1

        #1-3 row second column
        widget = QTextEdit(self)
        layout.addWidget(widget, 0, 2, 3, 2)
        label.setBuddy(widget)
        self.definitionEdit = widget

        #4th row
        label = QLabel(self, text='Transcription:')
        layout.addWidget(label, row, 0, alignment=Qt.AlignRight | Qt.AlignTop)

        widget = TranscriptionsWidget(self)
        widget.setMaximumHeight(label.sizeHint().height() * 4)
        layout.addWidget(widget, row, 1, 1, 3)
        label.setBuddy(widget)
        self.transcriptionEdit = widget
        row += 2

        #5th row
        label = QLabel(self, text='Examples:')
        layout.addWidget(label, row, 0, 1, 1, alignment=Qt.AlignRight | Qt.AlignTop)

        widget = ExamplesWidget(self)
        layout.addWidget(widget, row, 1, 2, 3)
        label.setBuddy(widget)
        self.examplesEdit = widget
        row += 2

    def _sortTranscriptions(self, transcriptions):
        # Set preferredTranscription as first transcription in list
        result = list(transcriptions)
        def key(entry):
            region, _ = entry
            if region == self._preferredRegion:
                return 0
            return 1

        result.sort(key=key)
        return result

    def ankiword(self):
        """Return shallow copy of previously setted ankiword with updated attributes."""
        # Don't modify saved ankiword - create copy
        if not self._ankiword:
            return None

        ankiword = copy.copy(self._ankiword)
        ankiword.lettering = str(self.letteringEdit.text())
        ankiword.hint = str(self.hintEdit.text())
        ankiword.partOfSpeech = str(self.partOfSpeechEdit.text())
        ankiword.definition = str(self.definitionEdit.toPlainText())

        # .entries returns copy
        ankiword.examples = self.examplesEdit.entries
        ankiword.transcriptions = self.transcriptionEdit.entries

        return ankiword

    def setAnkiword(self, newAnkiword):
        """Set new ankiword to widget."""
        self._ankiword = newAnkiword

        self.letteringEdit.setText(newAnkiword.lettering)
        self.hintEdit.setText(newAnkiword.hint)
        self.partOfSpeechEdit.setText(newAnkiword.partOfSpeech)
        self.definitionEdit.setText(newAnkiword.definition)

        self.transcriptionEdit.entries = self._sortTranscriptions(newAnkiword.transcriptions)
        self.examplesEdit.entries = newAnkiword.examples
