import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MetawordWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setupUI()

    def createMetawordLine(self):
        metawordLine = QLineEdit()
        metawordLine.setMinimumWidth(100)

        metawordRegExp = QRegExp('[A-Za-z]+([ -]([A-Za-z]+))*')
        validator = QRegExpValidator(metawordRegExp)
        metawordLine.setValidator(validator)

        return metawordLine
        
    def setupUI(self):
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.metawordLine = self.createMetawordLine()
        vbox.addWidget(self.metawordLine)
        vbox.addStretch(1)

        self.show()

