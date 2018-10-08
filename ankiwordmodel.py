"""This module defines AnkiwordModel subclass from TreeModel."""

from aqt.qt import Qt, QBrush, QColor, QGradient, QLinearGradient, QModelIndex
from .treemodel import TreeModel, TreeItem
from .textdistance import WordFreq

class AnkiwordModel(TreeModel):
    """Implementation of QAbstractItemModel for Ankiword list.

    This model maintain tree like structre for words grouping their by language and
    part of speach."""

    def __init__(self, parent=None, **kargs):
        super().__init__(parent, **kargs)
        self.rootItem = AnkiwordLevelItem(None)

    def data(self, index, role):
        """Overrided."""
        if not index.isValid():
            return ''

        if role == Qt.DisplayRole:
            return self.getItemByIndex(index).data(Qt.DisplayRole)
        if role == Qt.BackgroundRole:
            return self.getItemByIndex(index).data(role)
        return None

    def columnCount(self, parentIndex):
        """Overrided. Return 1 because there is only one column."""
        return 1

    def _nextLevel(self, levelName, parentIndex):
        """Find child with specified levelName or create new level."""
        for row in range(self.rowCount(parentIndex)):
            childIndex = self.index(row, 0, parentIndex)
            if levelName == childIndex.data():
                return childIndex
        # else create new level
        return self._appendLevel(levelName, parentIndex)

    def _appendLevel(self, levelName, parentIndex):
        parentLevelItem = self.getItemByIndex(parentIndex)
        newLevel = AnkiwordLevelItem(levelName, parentLevelItem)

        rows = self.rowCount(parentIndex)
        self.beginInsertRows(parentIndex, rows, rows)
        parentLevelItem.childs.append(newLevel)
        self.endInsertRows()

        return self.index(rows, 0, parentIndex)

    def _getAnkiwordParentIndex(self, ankiword):
        """Return parent level index for given ankiword."""
        languageLevelIndex = self._nextLevel(ankiword.language, QModelIndex())
        partOfSpeechLevelIndex = self._nextLevel(ankiword.partOfSpeech, languageLevelIndex)
        return partOfSpeechLevelIndex

    def addAnkiword(self, ankiword):
        """Add new ankiword at correct level."""
        parentIndex = self._getAnkiwordParentIndex(ankiword)

        parentLevel = parentIndex.internalPointer()
        childAnkiwords = [ankiwordItem.ankiword for ankiwordItem in parentLevel.childs]
        index = self._findAproppriateIndex(childAnkiwords, ankiword)

        self.beginInsertRows(parentIndex, index, index)
        parentLevel.childs.insert(index, AnkiwordItem(ankiword, parentLevel))
        self.endInsertRows()

        myIndex = self.index(index, 0, parentIndex)
        return myIndex

    def removeByIndex(self, index):
        """Remove Ankiword by index. It also removes empty parent level."""
        if not index.isValid():
            return

        parentIndex = self.parent(index)
        parentItem = self.getItemByIndex(parentIndex)

        row = index.row()

        self.beginRemoveRows(parentIndex, row, row)
        del parentItem.childs[row]
        self.endRemoveRows()

        if not parentItem.childs:
            self.removeByIndex(parentIndex)

    @staticmethod
    def _findAproppriateIndex(ankiwordList, newAnkiword):
        """Return index --- where is best place for new new Ankiword.

        Current heuristic algorithm:
        1. All new ankiword from web go to the end of list.
        2. If currently no element in list --- add to the end.
        3. Find ankiword that is the closest to the new ankiword (now "closest" mean closest in
        some word-freq metric) and add new ankiword after it.
        """
        if not newAnkiword.noteId or not ankiwordList:
            # if ankiword from web - append it to end
            return len(ankiwordList)

        newWordFreq = WordFreq(newAnkiword.definition)
        # save index and distance to that ankiword.definition
        indexWithDistance = [(i, newWordFreq.distance(WordFreq(ankiword.definition)))
                             for i, ankiword in enumerate(ankiwordList)]

        # compare by distance
        closestIndex = min(indexWithDistance, key=lambda k: k[1])[0]
        return closestIndex + 1 # because we want to insert item after closest by word distance

    def addAnkiwordList(self, ankiwordList):
        """Add new list of ankiword at correct levels."""
        for ankiword in ankiwordList:
            self.addAnkiword(ankiword)

    def resetAnkiwordList(self, ankiwordList):
        """Reset model and add new ankiwordList."""
        self.beginResetModel()
        self.rootItem = AnkiwordLevelItem(None)
        self.addAnkiwordList(ankiwordList)
        self.endResetModel()


class AnkiwordLevelItem(TreeItem):
    """Class used for grouping TreeItem."""

    def __init__(self, name, parentItem=None):
        TreeItem.__init__(self, parentItem)
        self.childs = []
        self.name = name

    def data(self, role=Qt.DisplayRole):
        """Return only self name"""
        if role != Qt.DisplayRole:
            return None
        return self.name

class AnkiwordItem(TreeItem):
    """TreeItem that hold particular Ankiword."""

    def __init__(self, ankiword, parentItem=None):
        TreeItem.__init__(self, parentItem)
        self.ankiword = ankiword

    def _getBrush(self):
        if not self.ankiword.noteId:
            return None
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor.fromRgbF(1, 1, 1, 0.0))
        gradient.setColorAt(1, QColor.fromRgbF(0, 1, 0, 0.5))
        return QBrush(gradient)

    def data(self, role=Qt.DisplayRole):
        """Return textual representation and background brush."""
        if role == Qt.BackgroundRole:
            return self._getBrush()

        if role == Qt.DisplayRole:
            text = ['<b>{0}</b>:'.format(self.ankiword.lettering)]
            if self.ankiword.hint:
                text.append('<i>({0})</i>'.format(self.ankiword.hint))
            text.append(self.ankiword.definition)
            return ' '.join(text)

        return None
