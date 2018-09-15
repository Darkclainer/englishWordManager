"""This module introduce AnkiwordModel view subclass from TreeMode.
It is abstract view for ankiword list
"""

from aqt.qt import Qt
from .treemodel import TreeModel, TreeItem
from .ankiword import Ankiword, metawordToAnkiwordList

class AnkiwordModel(TreeModel):
    """Display ankiword like tree. Word grouped by lanuage and part of speech"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootItem = AnkiwordLevelItem(None)

    def data(self, index, role):
        """Overrided."""
        if not index.isValid():
            return ''

        if role == Qt.DisplayRole:
            return self.getItemByIndex(index).data()
        if role == Qt.ToolTipRole:
            return self.getItemByIndex(index).data()
        return None

    def columnCount(self, parentIndex):
        """Overrided. Return 1 because there is only one column."""
        return 1

    def addAnkiword(self, ankiword):
        """Add new ankiword at correct level."""
        languageLevel = self.rootItem.nextLevel(ankiword.language)
        partOfSpeechLevel = languageLevel.nextLevel(ankiword.partOfSpeech)
        partOfSpeechLevel.childs.append(AnkiwordItem(ankiword, partOfSpeechLevel))

    def addAnkiwordList(self, ankiwordList):
        """Add new list of ankiword at correct levels."""
        for ankiword in ankiwordList:
            self.addAnkiword(ankiword)

    def setAnkiwordList(self, ankiwordList):
        """Reset model and add new ankiwordList."""
        self.beginResetModel()
        self.rootItem = AnkiwordLevelItem(None)
        self.addAnkiwordList(ankiwordList)
        self.endResetModel()


class AnkiwordLevelItem(TreeItem):
    """Class used to grouping TreeItem.
    self.levels - dictionary that map levels name and self.childs.
    """
    def __init__(self, name, parentItem=None):
        TreeItem.__init__(self, parentItem)
        self.childs = []
        self.levels = {}
        self.name = name

    def data(self):
        """Return only self name"""
        return self.name

    def nextLevel(self, levelName):
        """If there is levelName in self.levels - return it.
        Else create new AnkiwordLevelItem, save in dictionary and return it
        """
        if levelName not in self.levels:
            newLevel = AnkiwordLevelItem(levelName, self)
            self.childs.append(newLevel)
            self.levels[levelName] = newLevel
            return newLevel
        return self.levels[levelName]

class AnkiwordItem(TreeItem):
    """TreeItem that hold particular Ankiword."""
    def __init__(self, ankiword, parentItem=None):
        TreeItem.__init__(self, parentItem)
        self.ankiword = ankiword

    def data(self):
        """Return textual representation"""
        preambule = '<b>{0}</b>: '.format(self.ankiword.lettering)
        if self.ankiword.hint:
            return '{0}<i>({1})</i> {2}'.format(preambule,
                                                self.ankiword.hint,
                                                self.ankiword.definition)
        return '{0}{1}'.format(preambule, self.ankiword.definition)
