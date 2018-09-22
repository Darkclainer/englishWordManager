"""This module define function start that called on triggering action in anki menu"""
import aqt
from aqt import mw
from .mainwindow import MainWindow

def start():
    mw.englishWordManagerWindow = MainWindow()

    
