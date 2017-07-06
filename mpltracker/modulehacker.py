"""
modulehacker module

license: MIT
source: http://code.activestate.com/recipes/577740/

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
        # module is importing functions with the mpltracker. name which causes
        # everything to fail when installed.
        # This fixes https://github.com/kecnry/mpltracker/issues/1
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
