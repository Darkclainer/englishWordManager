"""This module define AnkiwordListWidget --- widget for viewing and managing ankiwords."""

from aqt.qt import QObject, QPersistentModelIndex, QModelIndex
from .treehtmlview import TreeHtmlView
from .ankiwordmodel import AnkiwordItem
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditordialog import AnkiwordEditorDialog

class AnkiwordListWidget(TreeHtmlView):
    """View and high level managing ankiword list.

    This widget like QListWidget but for ankiword list."""

    def __init__(self, parent=None, *, ankiInterface, **kargs):
        super().__init__(parent, **kargs)

        self.ankiInterface = ankiInterface
        self.setModel(AnkiwordModel())
        self._editorsManager = EditorsManager(self)

        self.clicked.connect(self.openEditor)
        self.destroyed.connect(self._editorsManager.closeAll)

    def openEditor(self, index):
        """Open new editor window for ankiword item."""
        if isinstance(index.internalPointer(), AnkiwordItem):
            self._editorsManager.openEditor(index)

    def resetAnkiwordList(self, ankiwordList):
        """Delete all previous ankiwords and add new."""
        self._editorsManager.closeAll()
        self.model().resetAnkiwordList(ankiwordList)
        self.expandAll()

    def addAnkiword(self, ankiword):
        """Add new ankiword to list."""
        return self.model().addAnkiword(ankiword)

    def removeByIndex(self, index):
        """Remove ankiword from list by index."""
        index = QModelIndex(index)
        self.model().removeByIndex(index)


class EditorsManager(QObject):
    """Manager for multiple AnkiwordEditorDialog windows."""

    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.ankiwordListWidget = parent
        # Keep editors in list because we need to find editor by assosiated to it
        # persistentIndex that can changes.
        self.editors = []

    def openEditor(self, index):
        """Open new editor dialog and bind it with index. If it's already opened --- pop up it."""
        persistentIndex = QPersistentModelIndex(index)
        editor = self.findEditor(persistentIndex)
        if editor:
            editor.activateWindow()
            return

        editor = AnkiwordEditorDialog(ankiwordListWidget=self.ankiwordListWidget)
        self.editors.append(editor)
        editor.closeDialog.connect(self.removeIndex) # remove itself when close
        editor.bound(index)
        editor.show()

    def findEditor(self, index):
        """Find particular editor dialog based on index."""
        for editor in self.editors:
            if editor.persistentIndex == index:
                return editor
        return None

    def closeAll(self):
        """Close all opened editor dialogs."""
        for editor in list(self.editors): # need list because it will be changed in time
            editor.close() # also it will remove it from list

    def removeIndex(self, index):
        """Remove window from list of current editor dialogs."""
        editor = self.findEditor(index)
        if editor:
            self.editors.remove(editor)
