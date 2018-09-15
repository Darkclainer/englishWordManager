"""This module define AnkiwordEditor widget, that used for editing Ankiword"""

from aqt.qt import (QWidget, QGridLayout, QLabel, QTextEdit,
                    QLineEdit, QComboBox, QAbstractItemView,
                    QListWidget, Qt)
from .exampleswidget import ExamplesWidget
from .transcriptionwidget import TranscriptionsWidget
#from .englishDictionary import Metaword, Suggestions

class AnkiwordEditor(QWidget):
    """Edit Ankiword.
    property ankiword for setting and getting Ankiword
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._ankiword = None#metawordToAnkiwordList(loadTestMetaword())[0]
        self.persistentIndex = None

        self._setupUi()

    def _setupUi(self):
        layout = QGridLayout()
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
        #widget = QListWidget(self)
        widget.setMaximumHeight(label.sizeHint().height() * 4)
        layout.addWidget(widget, row, 1, 1, 3)
        label.setBuddy(widget)
        self.transcriptionEdit = widget
        row += 2

        #5th row
        label = QLabel(self, text='Examples:')
        layout.addWidget(label, row, 0, 1, 1, alignment=Qt.AlignRight | Qt.AlignTop)

        widget = ExamplesWidget(self)
        #widget.setMaximumHeight(label.sizeHint().height() * 8)
        layout.addWidget(widget, row, 1, 2, 3)
        label.setBuddy(widget)
        self.examplesEdit = widget
        row += 2

    @property
    def ankiword(self):
        """Construct Ankiword from widget"""
        return self._ankiword

    @ankiword.setter
    def ankiword(self, newAnkiword):
        self._ankiword = newAnkiword
        
        self.letteringEdit.setText(newAnkiword.lettering)
        self.hintEdit.setText(newAnkiword.hint)
        self.partOfSpeechEdit.setText(newAnkiword.partOfSpeech)

        self.definitionEdit.setText(newAnkiword.definition)

        self.transcriptionEdit.entries = newAnkiword.transcriptions
        self.examplesEdit.entries = newAnkiword.examples
