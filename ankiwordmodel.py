"""This module introduce AnkiwordModel view subclass from TreeMode.
It is abstract view for ankiword list
"""

import aqt
from aqt.qt import Qt, QBrush, QColor, QGradient, QLinearGradient, QModelIndex
from .treemodel import TreeModel, TreeItem
from .ankiword import Ankiword, metawordToAnkiwordList
from .textdistance import WordFreq

class AnkiwordModel(TreeModel):
    """Display ankiword like tree. Word grouped by lanuage and part of speech"""
    def __init__(self, parent=None, **kargs):
        super().__init__(parent)
        self.rootItem = AnkiwordLevelItem(None)
        self.ankiInterface = kargs['ankiInterface']

    def data(self, index, role):
        """Overrided."""
        if not index.isValid():
            return ''

        if role == Qt.DisplayRole or role == Qt.ToolTipRole:
            return self.getItemByIndex(index).data(Qt.DisplayRole)
        if role == Qt.BackgroundRole:
            return self.getItemByIndex(index).data(role)
        return None

    def columnCount(self, parentIndex):
        """Overrided. Return 1 because there is only one column."""
        return 1

    def _nextLevel(self, levelName, parentIndex):
        for row in range(self.rowCount(parentIndex)):
            childIndex = self.index(row, 0, parentIndex)
            if levelName == childIndex.data():
                return childIndex
        else:
            # create new level
            return self._appendLevel(levelName, parentIndex)

    def _appendLevel(self, levelName, parentIndex):
        parentLevelItem = self.getItemByIndex(parentIndex)
        newLevel = AnkiwordLevelItem(levelName, parentLevelItem)

        rows = self.rowCount(parentIndex)
        self.beginInsertRows(parentIndex, rows, rows)
        parentLevelItem.childs.append(newLevel)
        self.endInsertRows()

        return self.index(rows, 0, parentIndex)

    def addAnkiword(self, ankiword):
        """Add new ankiword at correct level."""
        languageLevelIndex = self._nextLevel(ankiword.language, QModelIndex())
        partOfSpeechLevelIndex = self._nextLevel(ankiword.partOfSpeech, languageLevelIndex)

        partOfSpeechLevel = partOfSpeechLevelIndex.internalPointer()
        childAnkiwords = [ankiwordItem.ankiword for ankiwordItem in partOfSpeechLevel.childs]
        index = self._findAproppriateIndex(childAnkiwords, ankiword)

        self.beginInsertRows(partOfSpeechLevelIndex, index, index)
        partOfSpeechLevel.childs.insert(index, AnkiwordItem(ankiword, partOfSpeechLevel))
        self.endInsertRows()
        return self.index(index, 0, partOfSpeechLevelIndex)

    @staticmethod
    def _findAproppriateIndex(ankiwordList, newAnkiword):
        if not newAnkiword.noteId:
            # if ankiword from web - append it to end
            return len(ankiwordList)
        newWordFreq = WordFreq(newAnkiword.definition)
        # save index and distance to that ankiword.definition
        indexWithDistance = ((i, newWordFreq.distance(WordFreq(ankiword.definition))) 
                             for i, ankiword in enumerate(ankiwordList))
        indexWithDistance = list(indexWithDistance)
        # compare by distance
        newIndex = min(indexWithDistance, key=lambda k: k[1])[0]
        return newIndex + 1

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

    def data(self, role=Qt.DisplayRole):
        """Return only self name"""
        if role != Qt.DisplayRole:
            return None
        return self.name

    #def nextLevel(self, levelName):
        #"""If there is levelName in self.levels - return it.
        #Else create new AnkiwordLevelItem, save in dictionary and return it
        #"""
        #if levelName not in self.levels:
            #newLevel = AnkiwordLevelItem(levelName, self)
            #self.childs.append(newLevel)
            #self.levels[levelName] = newLevel
            #return newLevel
        #return self.levels[levelName]

class AnkiwordItem(TreeItem):
    """TreeItem that hold particular Ankiword."""
    def __init__(self, ankiword, parentItem=None):
        TreeItem.__init__(self, parentItem)
        self.ankiword = ankiword

    def _getBrush(self):
        if not self.ankiword.noteId:
            return None
        gradient = QLinearGradient(0,0, 1, 0)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor.fromRgbF(1,1,1,0))
        gradient.setColorAt(1, QColor.fromRgbF(0, 1, 0, 0.5))
        return QBrush(gradient) 

    def data(self, role=Qt.DisplayRole):
        """Return textual representation and background brush."""
        if role == Qt.BackgroundRole:
            return self._getBrush()
        elif role == Qt.DisplayRole:
            preambule = '<b>{0}</b>: '.format(self.ankiword.lettering)
            if self.ankiword.hint:
                return '{0}<i>({1})</i> {2}'.format(preambule,
                                                    self.ankiword.hint,
                                                    self.ankiword.definition)
            return '{0}{1}'.format(preambule, self.ankiword.definition)
        return None
