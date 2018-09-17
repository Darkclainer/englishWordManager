from aqt import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPersistentModelIndex
from .ankiwordeditor import AnkiwordEditor

class AnkiwordEditorHolder(QWidget):
    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self._index = None
        self._ankiwordEditor = None
        self._mainLayout = None
        self._buttonLayout = None
        self.setupUi()

    def bound(self, modelIndex):
        self._index = QPersistentModelIndex(modelIndex)
        ankiword = modelIndex.internalPointer().ankiword
        self._ankiwordEditor.ankiword = ankiword
        self._updateButtons(ankiword)

    def _clearButtonLayout(self):
        while self._buttonLayout.count():
            layoutItem = self._buttonLayout.takeAt(0)
            if layoutItem.widget():
                widget = layoutItem.widget()
                widget.setParent(None)
                widget.deleteLater()

    def _saveAnkiword(self):
        pass
    def _updateAnkiword(self):
        pass
    def _removeAnkiword(self):
        pass

    def _createButtonsForWebAnkiword(self):
        saveButton = QPushButton('Save', self)
        self._buttonLayout.addWidget(saveButton)

        self._buttonLayout.addStretch(1)

    def _createButtonsForLocalAnkiword(self):
        updateButton = QPushButton('Update', self)
        self._buttonLayout.addWidget(updateButton)

        removeButton = QPushButton('Remove', self)
        self._buttonLayout.addWidget(removeButton)

        self._buttonLayout.addStretch(1)

    def _updateButtons(self, ankiword):
        isAnkiwordSavedInDb = bool(ankiword.noteId)
        self._clearButtonLayout()

        if isAnkiwordSavedInDb:
            self._createButtonsForLocalAnkiword()
        else:
            self._createButtonsForWebAnkiword()

    def setupUi(self):
        layout = QVBoxLayout()
        self._mainLayout = layout
        self.setLayout(layout)

        self._ankiwordEditor = AnkiwordEditor(self)
        layout.addWidget(self._ankiwordEditor)
        
        self._buttonLayout = QHBoxLayout()
        layout.addLayout(self._buttonLayout)

