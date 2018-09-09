"""This module define TreeModel subclass of QAbstractItemMode.
TreeModel is simple realization of tree structure that use auxiliary TreeItem
"""

from aqt.qt import (QAbstractItemModel, QModelIndex)

class TreeItem:
    """Auxiliary class that hold tree structure of items.
    Subclass it and use in TreeModel
    """
    def __init__(self, parentItem):
        self.parentItem = parentItem
        self.childs = []

    @property
    def row(self):
        """Return on what row it sit"""
        if self.parentItem:
            return self.parentItem.childs.index(self)
        return 0

class TreeModel(QAbstractItemModel):
    """Simple realization of QAbstractItemModel for tree structure"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rootItem = None

    def getItemByIndex(self, index):
        """Return TreeItem by index.
        For invalid items returns self.root
        """
        if not index.isValid():
            return self.rootItem
        return index.internalPointer()

    def index(self, row, column, parentIndex):
        """Overrided Qt function."""
        if not self.hasIndex(row, column, parentIndex):
            return QModelIndex()

        parentItem = self.getItemByIndex(parentIndex)

        try:
            return self.createIndex(row, column, parentItem.childs[row])
        except IndexError:
            return QModelIndex()

    def parent(self, index):
        """Overrided Qt function."""
        if not index.isValid():
            return QModelIndex()

        parentItem = index.internalPointer().parentItem

        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row, 0, parentItem)

    def rowCount(self, parentIndex):
        """Overrided Qt function."""
        if parentIndex.column() > 0:
            return 0

        parentItem = self.getItemByIndex(parentIndex)

        return len(parentItem.childs)
