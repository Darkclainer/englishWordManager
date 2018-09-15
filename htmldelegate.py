"""This module define HTMLDeletate. Special delegate that can render html tags"""
from aqt.qt import (Qt, QStyledItemDelegate, QStyle, QApplication,
                    QTextOption, QTextDocument, QAbstractTextDocumentLayout,
                    QSize, QBrush, QColor, QTransform)

class HtmlDelegate(QStyledItemDelegate):
    """Delegate that can render html tags and can transform cell height to fit content"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.textDocument = QTextDocument()
        textOption = QTextOption()
        textOption.setWrapMode(QTextOption.WordWrap)
        self.textDocument.setDefaultTextOption(textOption)

    def _setupTextDocument(self, text, width):
        self.textDocument.setHtml(text)
        self.textDocument.setTextWidth(width)

    def paint(self, painter, option, index):
        """Overrided. Paint content."""
        text = index.data(Qt.DisplayRole)
        style = QApplication.style() if option.styleObject is None else option.styleObject.style()

        self._setupTextDocument(text, option.rect.width())

        option.text = ""
        option.backgroundBrush = index.data(Qt.BackgroundRole) or option.backgroundBrush
        style.drawControl(QStyle.CE_ItemViewItem, option, painter)

        ctx = QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, option)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        self.textDocument.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        """Overrided."""
        text = index.data(Qt.DisplayRole)
        treeView = option.styleObject
        width = treeView.columnWidth(0) - treeView.indentation() * 3

        self._setupTextDocument(text, width)
        return QSize(self.textDocument.idealWidth(), self.textDocument.size().height())
