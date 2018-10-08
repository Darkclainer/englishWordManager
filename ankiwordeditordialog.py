"""This module defines widget for actually managing single Ankiword - AnkiwordEditorDialog."""

import aqt
from aqt import (Qt, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                 QPersistentModelIndex, QModelIndex, pyqtSignal)
from .ankiwordattributeeditor import AnkiwordAttributeEditor
from .ankiinterface import AlreadySaved

class AnkiwordEditorDialog(QWidget):
    """Class for removing, updating or saving Ankiword.

    It's very coupled with AnkiwordListWidget.
    """

    closeDialog = pyqtSignal(QPersistentModelIndex)

    def __init__(self, parent=None, *, ankiwordListWidget, **kargs):
        super().__init__(parent, **kargs)

        self._ankiwordListWidget = ankiwordListWidget
        self._ankiInterface = ankiwordListWidget.ankiInterface
        self.persistentIndex = None
        self._ankiwordAttributeEditor = None
        self._buttonLayout = None
        self._setupUI()

    def keyReleaseEvent(self, event):
        """Overriden to close on esacpe."""
        if event.key() == Qt.Key_Escape:
            self.close()
            event.accept()
        else:
            super().keyReleaseEvent(event)

    def closeEvent(self, event):
        """Overrident to emit signal on close."""
        if self.persistentIndex:
            self.closeDialog.emit(self.persistentIndex)
        super().closeEvent(event)

    def bound(self, modelIndex):
        """Bound AnkiwordEditorDialog with particular item in model."""
        if not modelIndex.isValid():
            return
        self.persistentIndex = QPersistentModelIndex(modelIndex)
        ankiword = modelIndex.internalPointer().ankiword
        self._ankiwordAttributeEditor.setAnkiword(ankiword)
        self._updateButtons(ankiword)

    def _clearButtonLayout(self):
        """Delete subwidgets in layout."""
        while self._buttonLayout.count():
            layoutItem = self._buttonLayout.takeAt(0)
            if layoutItem.widget():
                widget = layoutItem.widget()
                widget.setParent(None)
                widget.deleteLater()

    def _saveAnkiword(self):
        if not self.persistentIndex or not self.persistentIndex.isValid():
            return
        ankiword = self._ankiwordAttributeEditor.ankiword()
        try:
            self._ankiInterface.saveAnkiword(ankiword)
        except AlreadySaved:
            msg = 'Word with definition: "{0}" already saved!'.format(ankiword.definition)
            aqt.utils.showInfo(msg)
            return
        newIndex = self._ankiwordListWidget.addAnkiword(ankiword)
        self.bound(newIndex)
        self._ankiwordListWidget.setCurrentIndex(newIndex)

    def _updateAnkiword(self):
        if not self.persistentIndex or not self.persistentIndex.isValid():
            return
        ankiword = self._ankiwordAttributeEditor.ankiword()
        if not ankiword.noteId:
            raise RuntimeError('Ankiword not currently saved - it can not updated!')

        self._ankiInterface.saveAnkiword(ankiword)

        # remove and add ankiword to list widget
        self._ankiwordListWidget.removeByIndex(self.persistentIndex)
        newIndex = self._ankiwordListWidget.addAnkiword(ankiword)
        self._ankiwordListWidget.setCurrentIndex(newIndex)
        self.bound(newIndex)

    def _removeAnkiword(self):
        if not self.persistentIndex or not self.persistentIndex.isValid():
            return

        self._ankiInterface.removeAnkiword(self._ankiwordAttributeEditor.ankiword())

        index = QModelIndex(self.persistentIndex)
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
        """Remove old layout and create new based on current ankiword."""
        isAnkiwordSavedInDb = bool(ankiword.noteId)
        self._clearButtonLayout()

        if isAnkiwordSavedInDb:
            self._createButtonsForLocalAnkiword()
        else:
            self._createButtonsForWebAnkiword()

    def _setupUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        preferredRegion = self._ankiInterface.config['preferredRegion']
        self._ankiwordAttributeEditor = AnkiwordAttributeEditor(self,
                                                                preferredRegion=preferredRegion)
        layout.addWidget(self._ankiwordAttributeEditor)

        self._buttonLayout = QHBoxLayout()
        layout.addLayout(self._buttonLayout)
