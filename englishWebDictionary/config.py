"""Define inteface for interacting with configuration."""
from aqt import mw

def getConfig():
    """Return current configuration."""
    return mw.addonManager.getConfig(__name__)

def setConfig(newConfig):
    """Set new configuration."""
    mw.addonManager.writeConfig(__name__, newConfig)
