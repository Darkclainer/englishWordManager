import aqt
from aqt import mw, QAction, QKeySequence
from .mainwindow import MainWindow
from . import startmodule

def start():
    startmodule.start()

def debugStart():
    import sys
    from . import debugreload
    debugreload.reloadAll(__name__)
    startmodule.start()

startAction = QAction("English word manager: start", mw)
startAction.setShortcut(QKeySequence('Ctrl+M'))
startAction.triggered.connect(debugStart)
mw.form.menuTools.addSeparator()
mw.form.menuTools.addAction(startAction)
