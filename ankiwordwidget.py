from aqt.utils import showInfo
from aqt.qt import (QObject, QWidget, QVBoxLayout, QPersistentModelIndex,
                    QModelIndex, Qt)
from .treehtmlview import TreeHtmlView
from .ankiwordmodel import AnkiwordModel
from .ankiwordeditorholder import AnkiwordEditorHolder

class AnkiwordWidget(TreeHtmlView):
    def __init__(self, ankiInterface, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.ankiInterface = ankiInterface
        model = AnkiwordModel(ankiInterface=ankiInterface)
        self.setModel(model)

        self.editorManager = EditorManager(self)

        self.doubleClicked.connect(self.doubleClickedSlot)

        self.destroyed.connect(self.editorManager.closeAll)

    def doubleClickedSlot(self, index):
        self.editorManager.openEditor(index)

    def resetAnkiwordList(self, ankiwordList):
        self.model().resetAnkiwordList(ankiwordList)
        self.expandAll()

    def addAnkiword(self, ankiword):
        return self.model().addAnkiword(ankiword)

    def removeByIndex(self, index):
        index = QModelIndex(index)
        self.model().removeByIndex(index)


class EditorManager(QObject):
    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)

        self.ankiwordWidget = parent
        self.editors = []

    def openEditor(self, index):
        persistentIndex = QPersistentModelIndex(index)
        editor = self.findEditor(persistentIndex)
        if editor:
            editor.activateWindow()
            return

        editor = AnkiwordEditorHolder(ankiwordWidget=self.ankiwordWidget)
        self.editors.append(editor)
        editor.closeEditor.connect(self.removeIndex)
        editor.bound(index)
        editor.show()

    def findEditor(self, index):
        for editor in self.editors:
            if editor.index == index:
                return editor
        return None

    def closeAll(self):
        for editor in list(self.editors):
            editor.close()

    def removeIndex(self, index):
        editor = self.findEditor(index)
        if editor:
            self.editors.remove(editor)

