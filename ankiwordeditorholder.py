import aqt
from aqt import (Qt, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                 QPersistentModelIndex, QModelIndex, pyqtSignal,
                 QAction)
from .ankiwordeditor import AnkiwordEditor
from .ankiinterface import AlreadySaved

class AnkiwordEditorHolder(QWidget):
    closeEditor = pyqtSignal(QPersistentModelIndex)

    def __init__(self, parent=None, *, ankiwordWidget, **kargs):
        super().__init__(parent, **kargs)

        self.ankiwordWidget = ankiwordWidget
        self.ankiInterface = ankiwordWidget.ankiInterface
        self.index = None
        self._ankiwordEditor = None
        self._mainLayout = None
        self._buttonLayout = None
        self.setupUi()

        #exitOnEsc = QAction('Close editor')
        #exitOnEsc.setShortcut(Qt.Key_B)
        #exitOnEsc.setShortcutContext(Qt.ApplicationShortcut)
        #exitOnEsc.triggered.connect(lambda: aqt.utils.showInfo('hello'))
        #self.addAction(exitOnEsc)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def closeEvent(self, event):
        if self.index:
            self.closeEditor.emit(self.index)
        super().closeEvent(event)

    def bound(self, modelIndex):
        self.index = QPersistentModelIndex(modelIndex)
        if not modelIndex.isValid():
            aqt.utils.showInfo('WHAT A FUCK!')
        ankiword = modelIndex.internalPointer().ankiword
        self._ankiwordEditor.setAnkiword(ankiword)
        self._updateButtons(ankiword)

    def _clearButtonLayout(self):
        while self._buttonLayout.count():
            layoutItem = self._buttonLayout.takeAt(0)
            if layoutItem.widget():
                widget = layoutItem.widget()
                widget.setParent(None)
                widget.deleteLater()

    def _saveAnkiword(self):
        if not self.index or not self.index.isValid():
            return
        ankiword = self._ankiwordEditor.ankiword()
        try:
            self.ankiInterface.saveAnkiword(ankiword)
        except AlreadySaved as e:
            msg = 'Word with definition: "{0}" already saved!'.format(ankiword.definition)
            aqt.utils.showInfo(msg)
            return
        newIndex = self.ankiwordWidget.addAnkiword(ankiword)
        self.bound(newIndex)
        self.ankiwordWidget.setCurrentIndex(newIndex)

    def _updateAnkiword(self):
        if not self.index or not self.index.isValid():
            return
        ankiword = self._ankiwordEditor.ankiword()
        self.ankiInterface.saveAnkiword(ankiword)

        self.ankiwordWidget.removeByIndex(self.index)
        newIndex = self.ankiwordWidget.addAnkiword(ankiword)
        self.bound(newIndex)
        self.ankiwordWidget.setCurrentIndex(newIndex)

    def _removeAnkiword(self):
        if not self.index or not self.index.isValid():
            return
        
        self.ankiInterface.removeAnkiword(self._ankiwordEditor.ankiword())

        index = QModelIndex(self.index)
        index.model().removeByIndex(index)
        #self.index = None
        self.close()

    def _createButtonsForWebAnkiword(self):
        saveButton = QPushButton('Save', self)
        saveButton.clicked.connect(self._saveAnkiword)
        self._buttonLayout.addWidget(saveButton)

        self._buttonLayout.addStretch(1)

    def _createButtonsForLocalAnkiword(self):
        updateButton = QPushButton('Update', self)
        updateButton.clicked.connect(self._updateAnkiword)
        self._buttonLayout.addWidget(updateButton)

        removeButton = QPushButton('Remove', self)
        removeButton.clicked.connect(self._removeAnkiword)
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

