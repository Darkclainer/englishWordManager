"""This module define TranscriptionsWidget and TranscriptionsModel for editing transcriptions
of ankiword.
"""
from aqt.qt import Qt
from .movablelist import MovableListModel, MovableListWidget
from .htmldelegate import HtmlDelegate

class TranscriptionsDelegate(HtmlDelegate):
    """Special delegate to deal with (region, transcription) format of entries
    in transcriptions."""

    def setEditorData(self, widget, index):
        """Overrided."""
        region, transcription = index.data(Qt.EditRole)
        widget.setText(transcription)

    def setModelData(self, widget, model, index):
        """Overrided."""
        region, transcription = index.data(Qt.EditRole)
        newEntry = (region , str(widget.text()))
        model.setData(index, newEntry, Qt.EditRole)
        

class TranscriptionsWidget(MovableListWidget):
    """Subclass of MovableListWidget, the only purpose - set TranscriptionsModel as model."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModel(TranscriptionsModel())
        self.setItemDelegate(TranscriptionsDelegate())

class TranscriptionsModel(MovableListModel):
    """Subclass of MovableListModel. Override defaultEntry, data, setData to confirm
    transcription format."""

    defaultEntry = ('', '')

    def _formatEntry(self, row):
        region, transcription = self._entries[row]
        return '<b>{0}:</b> {1}'.format(region, transcription)

    def data(self, index, role):
        """Overrided."""
        if not index.isValid():
            return ''

        if role == Qt.DisplayRole:
            if index.row() < 1:
                return '<i>({0})</i> {1}'.format(index.row() + 1, self._formatEntry(index.row()))
            return self._formatEntry(index.row())

        if role == Qt.EditRole:
            return self._entries[index.row()]
        return None


    def setData(self, index, value, role):
        """Overrided."""
        if not index.isValid():
            return False

        #region, transcription = value
        self._entries[index.row()] = value
        return True
