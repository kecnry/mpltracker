"""
decorations module

license: MIT
source: http://code.activestate.com/recipes/577742-apply-decorators-to-all-functions-in-a-module/

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

import types
import modulehacker

_modules = {}
_decorators = []
def register(decorator, modules=None):
    """Register a decorator for a list of module names."""
    if not decorator:
        return
    if not modules and decorator in _decorators:
        return
    if not modules:
        _decorators.append(decorator)
        return

    if isinstance(modules, str):
        modules = (modules,)
    for module in modules:
        if module not in _modules:
            _modules[module] = []
        _modules[module].append(decorator)

class Hacker(modulehacker.Hacker):
    def hack(self, module):
        for decorator in _modules.get(module.__name__, ()):
            self.decorate(module, decorator)
        for decorator in _decorators:
            self.decorate(module, decorator)
        return module
    def decorate(self, module, decorator):
        for attr in module.__dict__:
            obj = getattr(module, attr)
            if isinstance(obj, types.FunctionType):
                setattr(module, attr, decorator(obj))

modulehacker.register(Hacker())
