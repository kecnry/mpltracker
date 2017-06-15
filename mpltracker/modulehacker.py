"""
modulehacker module

license: MIT
source: http://code.activestate.com/recipes/577740/
"""

import sys
import importlib

_hackers = []
def register(obj):
    _hackers.append(obj)

class Hacker:
    def hack(self, module):
        return module

class Loader:
    def __init__(self):
        self.module = None

    def find_module(self, name, path):
        # print "*** modulehacker.find_module", name, path
        sys.meta_path.remove(self)
        # not entirely sure why this is necessary, but the parent mpltracker
        # module is import functions with the mpltracker. name which causes
        # everything to fail when installed.  This fixes https://github.com/kecnry/mpltracker/issues/1
        if 'mpltracker.' in name:
            name = '.'.join(name.split('.')[1:])
        self.module = importlib.import_module(name)
        sys.meta_path.insert(0, self)
        return self

    def load_module(self, name):
        # print "*** modulehacker.load_module", name
        if not self.module:
            raise ImportError("Unable to load module.")
        module = self.module
        for hacker in _hackers:
            module = hacker.hack(module)
        sys.modules[name] = module
        return module

sys.meta_path.insert(0, Loader())
