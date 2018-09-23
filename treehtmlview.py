"""This module define TreeHtmlView"""
from aqt.qt import (QTreeView)
from .htmldelegate import HtmlDelegate

class TreeHtmlView(QTreeView):
    """Like simple QTreeView, but uses HtmlDelegate to render cells."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setItemDelegate(HtmlDelegate())

    def resizeEvent(self, event):
        """Overrided. On resize width can changed so and cell width."""
        QTreeView.resizeEvent(self, event)
        self.model().layoutChanged.emit()
