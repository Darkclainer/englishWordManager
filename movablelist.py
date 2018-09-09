"""This module define two classes: MovableListWidget which subclasses must be used together."""

from aqt.qt import (Qt, QAbstractItemView, QAbstractListModel, QListView, QAction,
                    QModelIndex)
from .htmldelegate import HtmlDelegate

class MovableListWidget(QListView):
    """View for subclass MovableListModel.
    In __init__ you must set correct model.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable internal drag-move features
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)

        self.setItemDelegate(HtmlDelegate())

        self._createActions()
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def _makeSelectedFirst(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        model = self.model()
        savedData = model.data(index, Qt.EditRole)
        model.removeRows(index.row(), 1, QModelIndex())
        model.insertRows(0, 1, QModelIndex())
        firstIndex = model.index(0, 0)
        model.setData(firstIndex, savedData, Qt.EditRole)

    def _addNewItem(self):
        model = self.model()
        model.insertRows(0, 1, QModelIndex())
        self.edit(model.index(0, 0))

    def _createActions(self):
        makeFirst = QAction('Set item first', self)
        makeFirst.setShortcut(Qt.Key_1)
        makeFirst.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        makeFirst.triggered.connect(self._makeSelectedFirst)
        self.addAction(makeFirst)

        add = QAction('Add item', self)
        add.setShortcut(Qt.Key_A)
        add.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        add.triggered.connect(self._addNewItem)
        self.addAction(add)

    def columnWidth(self, *pargs):
        """Declared for compatibility with HtmlDelegate."""
        return self.width()

    def indentation(self):
        """Declared for compatibility with HtmlDelegate."""
        return 0

    @property
    def entries(self):
        """Set and get property for list of entries, on which widget operates."""
        return self.model().entries

    @entries.setter
    def entries(self, anotherEntries):
        self.model().entries = anotherEntries

class MovableListModel(QAbstractListModel):
    """Class that allow user to work with list of entries.
    Entries can be edited and dragged around.
    You can change default entry value by attribute self.defaultEntry.
    """
    defaultEntry = ''

    def __init__(self, parent=None):
        super().__init__(parent)

        self._entries = []

    @property
    def entries(self):
        """Get/set entries element. Entries must iterable object"""
        return list(self._entries)

    @entries.setter
    def entries(self, anotherEntries):
        self.beginResetModel()
        self._entries = list(anotherEntries)
        self.endResetModel()

    def rowCount(self, index):
        """Overrided. Return number of entries."""
        if index.isValid():
            return 0
        return len(self._entries)

    def insertRows(self, row, count, parentIndex):
        """Overrided."""
        self.beginInsertRows(parentIndex, row, row + count - 1)
        self._entries[row:row] = [self.defaultEntry] * count
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parentIndex):
        """Overrided."""
        self.beginRemoveRows(parentIndex, row, row + count - 1)
        del self._entries[row:row+count]
        self.endRemoveRows()
        return True

    def supportedDropActions(self):
        """Overrided."""
        return Qt.MoveAction

    def flags(self, index):
        """Overrided."""
        defaultFlags = QAbstractListModel.flags(self, index) | Qt.ItemIsEditable

        if index.isValid():
            return Qt.ItemIsDragEnabled |  defaultFlags
        return Qt.ItemIsDropEnabled | defaultFlags
