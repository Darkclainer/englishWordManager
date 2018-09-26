import aqt
from aqt import mw

def getConfig():
    return mw.addonManager.getConfig(__name__)

def setConfig(newConfig):
    mw.addonManager.writeConfig(__name__, newConfig)
