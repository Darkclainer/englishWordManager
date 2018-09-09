"""This module define AnkiwordView"""
from .treehtmlview import TreeHtmlView
from .ankiwordmodel import AnkiwordItem

class AnkiwordView(TreeHtmlView):
    """AnkiwordView is like TreeHtmlView but with editor on click."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.getEditor = lambda: None
        self.clicked.connect(self.clickedSlot)

    def clickedSlot(self, index):
        """Create editor."""
        editor = self.getEditor()
        if not editor:
            return

        item = index.internalPointer()
        if isinstance(item, AnkiwordItem):
            editor.ankiword = item.ankiword
