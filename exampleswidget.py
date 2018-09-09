"""This module defines ExamplesWidget and ExamplesModel for editing examples in ankiword."""
from aqt.qt import Qt
from .movablelist import MovableListModel, MovableListWidget

class ExamplesWidget(MovableListWidget):
    """Almost like MovableListWidget, but use ExamplesModel as model."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(ExamplesModel())

class ExamplesModel(MovableListModel):
    """This class define data and setData method for work with examples."""
    def data(self, index, role):
        """Overrided. Show number of examples that will be added."""
        if not index.isValid():
            return ''

        if role == Qt.DisplayRole:
            if index.row() < 2:
                return '<i>({0})</i> {1}'.format(index.row() + 1, self._entries[index.row()])
            return self._entries[index.row()]

        if role == Qt.EditRole:
            return self._entries[index.row()]
        return None


    def setData(self, index, value, role):
        """Overrided."""
        if not index.isValid():
            return False

        self._entries[index.row()] = str(value)
        return True
