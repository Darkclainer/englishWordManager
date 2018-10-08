"""This module for debug purpose only.

It defines function reloadAll that recursively reloads modules."""
import sys
import importlib
import types

def reloadAll(moduleName):
    permitted = {module for module in sys.modules.values()
                 if module.__name__.startswith(moduleName)}
    # delete self
    permitted.remove(sys.modules[__name__])
    # delete __init__
    permitted.remove(sys.modules[moduleName])

    _reloadRecursive(sys.modules[moduleName], permitted, set())

def _tryReload(module):
    try:
        importlib.reload(module)
        #sys.stderr.write('Reloaded: {0}\n'.format(module.__name__))
    except Exception as exception:
        msg = 'FAILED load module: "{0}". Exception: {1}'.format(module.__name__,
                                                                 str(exception))
        sys.stderr.write(msg)

def _reloadInnerModule(module, permitted, reloaded):
    if module in permitted and module not in reloaded:
        _reloadRecursive(module, permitted, reloaded)

def _reloadRecursive(module, permitted, reloaded):
    reloaded.add(module)

    for obj in module.__dict__.values():
        if isinstance(obj, types.ModuleType):
            _reloadInnerModule(obj, permitted, reloaded)

        elif hasattr(obj, '__module__'):
            innerModule = sys.modules[getattr(obj, '__module__')]
            _reloadInnerModule(innerModule, permitted, reloaded)

    if module in permitted:
        _tryReload(module)
