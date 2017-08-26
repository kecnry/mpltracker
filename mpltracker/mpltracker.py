#!/usr/bin/python

_current = None
_intercept = False
_intercept_user = False

_trackers = {}

import decorations
import functools

try:
    from astropy.table import Table, Column
except ImportError:
    _has_astropy = False
else:
    _has_astropy = True

def intercept_func(fctn):
    """
    this is a decorator, which when attached to a function will pass
    that function through mpltr.add()

    """
    @functools.wraps(fctn)
    def call(*args, **kwargs):
        global _intercept
        global _trackers
        if _intercept:
            # print "intercept_func enabled", fctn
            _intercept = False
            # for the sake of getting the right tracker, we need to see if
            # the plt.* command is acting on a stored object
            if plt.gcf() in _trackers.keys():
                obj = plt.gcf()
            elif plt.gca() in _trackers.keys():
                obj = plt.gca()
            else:
                obj = None
            return_ = add(obj, fctn, *args, **kwargs)
            _intercept = True
            return return_
        else:
            # print "intercept_func disabled", fctn
            return fctn(*args, **kwargs)

    return call

def intercept_method(obj, fctn):
    """
    this is a decorator, which when attached to a method of an object will pass
    that function through mpltr.add()

    """
    # extra argument needed because of this bug: http://bugs.python.org/issue3445
    @functools.wraps(fctn, set(['__doc__']))
    def call(*args, **kwargs):
        global _intercept
        if _intercept:
            # print "intercept_method enabled", obj, fctn
            _intercept = False
            return_ = add(obj, fctn, *args, **kwargs)
            _intercept = True
            return return_
        else:
            # print "intercept_method disabled", obj, fctn
            return fctn(*args, **kwargs)

    return call

def attach_decorators_to_object(obj):
    recursive_names = []
    #~ recursive_names = ['canvas']
    # canvas causes problem with exit not being able to disconnect

    for name, fn in inspect.getmembers(obj):
        if isinstance(fn, types.UnboundMethodType):
            # fn is original method of obj
            new_method = intercept_method(obj, fn)
            # now override so that the decorator will always be called
            setattr(obj, name, new_method)
        elif isinstance(fn, types.ObjectType) and name in recursive_names:
            # recursively call this function again
            attach_decorators_to_object(fn)


def disable_intercept(fctn):
    """
    this is a decorator which should wrap any internal function that calls plt
    it will temporarily disable intercepting so we don't get caught in an infinite loop
    """
    @functools.wraps(fctn)
    def call(self, *args, **kwargs):
        global _intercept
        _intercept = False
        return_ = fctn(self, *args, **kwargs)
        _intercept = _intercept_user
        return return_
    return call


# attach decorator to matplotlib function calls
# later we'll attach the decorator to any returned object
decorations.register(intercept_func, "matplotlib.pyplot")

# in order to hack the classes in matplotlib.collections, we first need to
# hack anything that may subclass those classes... which is a bit ugly and
# surely could break some unforseen things
decorations.register(intercept_func, "mpl_toolkits.mplot3d.art3d")
decorations.register(intercept_func, "mpl_toolkits.axes_grid.anchored_artists")
decorations.register(intercept_func, "matplotlib.collections")
decorations.register(intercept_func, "matplotlib.colors")

import numpy as np
import os, sys

import matplotlib
if 'DISPLAY' not in os.environ.keys() and sys.platform not in ['win32','cygwin']:
    matplotlib.use('Agg')
elif hasattr(sys, 'real_prefix'):
    # then we're likely in a virtualenv.  Our best bet is to use the 'TkAgg'
    # backend, but this will require python-tk to be installed on the system
    matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d
import mpl_toolkits.axes_grid.anchored_artists
import matplotlib.collections
import matplotlib.colors

import inspect, types
import json
import base64
import urllib2

class JSONEncoder(json.JSONEncoder):
    """
    https://stackoverflow.com/questions/3488934/simplejson-and-numpy-array
    """

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)

        if inspect.isclass(obj):
            return dict(__module__=obj.__module__, __class__=obj.__name__)

        # Let the base class default method raise the TypeError
        return super(JSONEncoder, self).default(obj)

def json_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    https://stackoverflow.com/questions/3488934/simplejson-and-numpy-array

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])

    # elif isinstance(dct, dict) and '__module__' in dct:
        # print "***", dct, getattr(sys.modules[dct['__module__']], dct['__class__'])
        # return getattr(sys.modules[dct['__module__']], dct['__class__'])

    return dct

def _id(obj):
    if (isinstance(obj, str) or isinstance(obj, unicode)) and obj[0:4]=='<id:':
        return obj
    elif obj is None:
        return None
    elif obj is plt:
        return None
    else:
        return '<id:{}>'.format(id(obj))

def _getobject(obj, available_objects):
    if (isinstance(obj, str) or isinstance(obj, unicode)) and obj[0:4]=='<id:':
        return available_objects.get(obj)
    else:
        return obj

class MPLPlotCommand(object):
    """
    class that holds all the information necessary to execute a single mpl command
    """
    def __init__(self, obj, func, *args, **kwargs):
        if hasattr(func, 'func_name'):
            func = func.func_name

        self._obj = _id(obj)
        self._func = func
        self._args = args
        self._returns = kwargs.pop('returns', [])
        self._kwargs = kwargs

    def __repr__(self):
        return '<MPLPlotCommand {}>'.format(self.func)

    def __str__(self):
        return '{} = {}.{}(*{}, **{})'.format(self.returns, self.obj, self.func, self.args, self.kwargs)

    @property
    def __dict__(self):
        return {'returns': self._returns, 'obj': self._obj, 'func': self._func, 'args': self._args, 'kwargs': self._kwargs}

    @property
    def obj(self):
        if self._obj is None:
            if isinstance(self.func, types.TypeType):
                return None
            else:
                return plt
        else:
            return self._obj

    @property
    def func(self):
        if isinstance(self._func, dict) and '__module__' in self._func:
            return getattr(sys.modules[self._func['__module__']], self._func['__class__'])
        else:
            return self._func

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def returns(self):
        return self._returns

    def run(self, obj=None, available_objects={}):
        # print "MPLPlotCommand.run", obj, self.func, self.args, self.kwargs

        # parse args and kwargs to see if within available_objects
        args = list(self.args)
        for i,arg in enumerate(args):
            args[i] = _getobject(arg, available_objects)

        kwargs = self.kwargs
        for k,v in kwargs.items():
            kwargs[k] = _getobject(v, available_objects)

        obj = _getobject(obj, available_objects)

        if isinstance(self.func, types.TypeType) or isinstance(self.func, types.FunctionType):
            # then forget obj, we want to instantiate self.func
            ret = self.func(*args, **kwargs)

        else:

            if obj is None:
                obj = plt

            ret = getattr(obj, self.func)(*args, **kwargs)

        return ret

class MPLTracker(object):
    """
    class that holds multiple MPLPlotCommand objects and handles passing
    any objects that are returned from one command and later passed to another
    """
    def __init__(self, load=None, set_as_current=True):
        if set_as_current:
            global _current
            _current = self

        # commands holds an ordered list of MPLPlotCommand objects
        self.commands = []
        # returns holds a dictionary of id, object pairs returned by plotting calls
        self.available_objects = {}
        # used returns holds a list of the id's of returned objects that are actually used
        self.used_objects = []

        # TODO: handle args smarter so we don't store duplicates for arrays ?
        #   this would require storing data in the MPLTracker instead of the MPLCommand

        if load is not None:
            if isinstance(load, file):
                data = f.readline()
            if os.path.isfile(load):
                f = open(load, 'r')
                data = f.readline()
            else:
                try:
                    # maybe we were passed a url
                    data = urllib2.urlopen(load).read()
                except ValueError:
                    # as last resort: maybe we were passed the json string itself
                    data = load

            for cdict in json.loads(data, object_hook=json_obj_hook):
                self.commands.append(MPLPlotCommand(cdict['obj'], cdict['func'], *cdict['args'], returns=cdict['returns'], **cdict['kwargs']))

    @classmethod
    def init_object(cls, func_to_create_obj, *args, **kwargs):
        """
        """
        tracker = cls(set_as_current=False)
        ret_obj = tracker.add(func_to_create_obj, *args, **kwargs)
        global _trackers
        _trackers[ret_obj] = tracker

        return tracker, ret_obj

    def list_commands(self):
        """
        quick summary of all commands that have been tracked
        """
        string = ''
        for command in self.commands:
            # TODO: make this nicer - problem is after saving we lose the actual returns
            # perhaps we could also store their names?
            string += "{}\n".format(command.func)
        return string

    def get_data(self):
        """
        get all data (args) from all commands that have been tracked
        """
        lst = []
        for command in self.commands:
            # TODO: this makes the assumption of xy data... we may need to be
            # more clever for other plotting types

            # TODO: we are also assuming that data is always sent as args (not
            # kwargs)
            lst.append([command.args[0], command.args[1]])

        return lst

    def get_data_table(self, format=None):
        """
        get all data (args) from all commands that have been tracked and return
        an astropy table instance
        """
        if not _has_astropy:
            raise ImportError("could not import astropy.table.Table")

        t = Table()

        # For now let's only support plot with a single dataset.  Its difficult
        # otherwise to deal with different lengthed columns.
        if len(self.commands) != 1:
            print self.commands
            raise NotImplementedError("currently only supports 1 dataset (you have {})".format(len(self.commands)))

        for command in self.commands:
            # TODO: this makes the assumption of xy data... we may need to be
            # more clever for other plotting types

            # TODO: we are also assuming that data is always sent as args (not
            # kwargs)

            # TODO: get column names from the datalabels or axes labels
            # TODO: units, etc
            xinfo = {}
            xinfo['data'] = command.args[0]
            xinfo['name'] = 'x'
            t.add_column(Column(**xinfo))


            yinfo = {}
            yinfo['data'] = command.args[1]
            yinfo['name'] = 'y'
            t.add_column(Column(**yinfo))

        if format is None:
            return t
        else:
            return t.write(sys.stdout, format)

    def add(self, func, *args, **kwargs):
        """
        add exactly as it would be called from matplotlib.pyplot (plt)

        examples:
        plt.plot(a,b,'k.') => mpltr.add(plt.plot, a, b, 'k.')

        fig = plt.figure() => fig = mpltr.add(plt.figure)
        ax = fig.add_subplot(111) => ax = mpltr.add(fig.add_subplot, (111))
        """
        if hasattr(func, 'im_self'):
            # then func is an attribute of some obj that we hopefully
            # have stored in self.returns
            if func.im_self in self.available_objects.values():
                # then the obj was a return from a previous command
                obj = func.im_self

                # we need to remember to track this connection when saving
                self.used_objects.append(_id(obj))

            else:
                # raise ValueError("mpltracker cannot find object: {}".format(func.im_self))
                # then we'll just call this as normal
                # TODO: add logger warning?
                # print "skipping tracking for call on {}".format(func.im_self)
                return func(*args, **kwargs)

        else:
            # default to func being an attribute of plt
            # TODO: handle more options
            #   from matplotlib import collections
            #   from mpl_toolkits.mplot3d import art3d
            #   different ways to import plt?
            obj = plt

        # parse args and kwargs for items already being tracked
        args = list(args)
        for i,arg in enumerate(args):
            idarg = _id(arg)
            if idarg in self.available_objects.keys():
                args[i] = idarg
                self.used_objects.append(idarg)

        for k,v in kwargs.items():
            idkwarg = _id(v)
            if idkwarg in self.available_objects.keys():
                kwargs[k] = idkwarg
                self.used_objects.append(idkwarg)

        comm = MPLPlotCommand(obj, func, *args, **kwargs)
        self.commands.append(comm)

        # we need to run this command so we can track the output
        ret = comm.run(obj, self.available_objects)

        if not (isinstance(ret, list) or isinstance(ret, tuple)):
            ret_ = (ret,)
        else:
            ret_ = ret

        for ri in ret_:
            # now we need to attach the intercept decorator to any method on the
            # returned object
            attach_decorators_to_object(ri)

            comm.returns.append(_id(ri))
            self.available_objects[_id(ri)] = ri

        # add all items to be tracked by this tracker
        global _trackers
        if obj!=plt and obj in _trackers.keys():
            for ri in ret_:
                _trackers[ri] = self

        # return as if the user was making the call directly
        return ret

    def save(self, filename=None):
        # purge not-needed returns
        #    clear all command.returns if not in self.used_objects
        #    clear self.available_objects
        #    clear self.used_objects

        for command in self.commands:
            for i,return_ in reversed(list(enumerate(command.returns))):
                if return_ not in self.used_objects:
                    command.returns[i] = '<id:UNUSED>'

        self.available_objects = {}
        self.used_objects = []

        dump = json.dumps([c.__dict__ for c in self.commands], cls=JSONEncoder)

        if filename is not None:
            f = open(filename, 'w')
            f.write(dump)
            f.close()
            return filename
        else:
            # just return the json string
            return dump

    @disable_intercept
    def get_fig(self):
        for i,command in enumerate(self.commands):
            # print i
            obj = _getobject(command.obj, self.available_objects)

            ret = command.run(obj, self.available_objects)

            if not (isinstance(ret, list) or isinstance(ret, tuple)):
                ret_ = (ret,)
            else:
                ret_ = ret

            # now assign to the expected output ids
            for ri,return_ in zip(ret_, command.returns):
                self.available_objects[return_] = ri

        return plt.gcf()

    @disable_intercept
    def show(self):
        fig = self.get_fig()
        plt.show()
        return None

def axes(*args, **kwargs):
    """
    create a new mpl axes and track only that object (and its children)
    """
    intercept(False)  # TODO: not sure if this is the best way
    mpltr, mplfig = MPLTracker.init_object(plt.figure, *args, **kwargs)
    intercept(True)
    mplax = mplfig.add_subplot(111)
    return mplax

def figure(*args, **kwargs):
    """
    create a new mpl figure and track only that object (and its children)
    """
    intercept(False)  # TODO: not sure if this is the best way
    mpltr, mplfigure = MPLTracker.init_object(plt.figure, *args, **kwargs)
    intercept(True)
    return mplfigure

def close(obj):
    if not isinstance(obj, MPLTracker):
        mpltr = gct(obj)

        # close the matplotlib object
        try:
            plt.close(obj)
        except:
            pass
    else:
        mpltr = obj

    global _current
    global _trackers

    if _current == mpltr:
        _current = None

    for k,v in _trackers.items():
        if v == mpltr:
            del _trackers[k]

    del mpltr


def intercept(on=True):
    """
    enable or disable tracking/interecpting of matplotlib calls
    """
    global _intercept, _intercept_user
    _intercept = on
    _intercept_user = on

def start():
    """
    intercept(True)
    """
    # if obj is not None:
        # mpltr = MPLTracker()

    intercept(True)

    return gct(obj=None)

def stop():
    """
    intercept(False)
    """
    intercept(False)

def gct(obj=None):
    """
    get current tracker
    """
    if _current is None:
        mpltr = MPLTracker()

    if obj is None:
        return _current
    else:
        return _trackers.get(obj, _current)

def list_commands():
    """
    global call to mpltr.list_commands
    """
    return gct().list_commands()

def show(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    open an interactive matplotlib window
    """
    if load is not None:
        mpltr = MPLTracker(load)

    gct().show()

def get_fig(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the figure object
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_fig()

def get_data(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the data associated with that figure
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_data()

def get_data_table(load=None):
    """
    load a figure from a JSON string, URL, or filename and immediately
    return the data associated with that figure
    """
    if load is not None:
        mpltr = MPLTracker(load)

    return gct().get_data_table()

def write_data_table(load=None, filename='table.data', format='ascii.ecsv'):
    """
    """
    return get_data_table(load=load).write(filename, format=format)

def add(obj, func, *args, **kwargs):
    """
    global call to mpltr.add
    """
    if _current is None:
        mpltr = MPLTracker()

    return gct(obj).add(func, *args, **kwargs)

def save(filename=None, stop_intercept=True):
    """
    global call to mpltr.save
    """
    if stop_intercept:
        stop()
    return gct().save(filename=filename)

if __name__ == '__main__':
    show(sys.argv[1])
