# mpltracker

This module intercepts all calls to [matplotlib](https://github.com/matplotlib/matplotlib) and then allows you to do any of the following:
* save the figure to a json-formatted file which can then be reloaded
* show or save the image
* access the data arrays
* export the arrays to an ecsv file formatted to submit directly to the journals (work in progress)

**NOTE:** mpltracker is still a work in progress and so the API may change at any time.

## Dependencies

* [matplotlib](https://github.com/matplotlib/matplotlib)
* [numpy](https://github.com/numpy/numpy)
* [astropy](https://github.com/astropy/astropy) (optional - used for exporting to tables)

Currently mpltracker has been tested on Python 2.7 with matplotlib 1.5.2.  There is currently an [open issue](https://github.com/kecnry/mpltracker/issues/2) to create nosetests and test on multiple version of Python/matplotlib.

## Installation

Installation is done using the standard python setup.py commands.

To install globally:
```
python setup.py build
sudo python setup.py install
```

Or to install locally:
```
python setup.py build
python setup.py install --user
```

## Basic Usage

mpltracker is imported as a python module, but **must** be imported before the first import to matplotlib

```
import mpltracker
import matplotlib.pyplot as plt
```

By calling start, the tracker will then start 'spying' and recording all commands sent through matplotlib

```
mpltracker.start()
```

To stop tracking, simply issue the stop command

```
mpltracker.stop()
```

To save the output to a file

```
mpltracker.save(filename)
```

To show the figure(s) currently tracked

```
mpltracker.show()
```

or to load in and show a previously saved file

```
mpltracker.show(filename)
```

For more details, see the example scripts in the examples directory:
* [simple](https://github.com/kecnry/mpltracker/blob/master/examples/simple.py)
* [subplots](https://github.com/kecnry/mpltracker/blob/master/examples/subplots.py)
* [multiple simultaneous trackers](https://github.com/kecnry/mpltracker/blob/master/examples/multiple_trackers.py)
* [data-behind-the-figure](https://github.com/kecnry/mpltracker/blob/master/examples/data_behind_figure.py)

## Command-line usage

Installing mpltracker also installs a command-line utility called `mplshow`.  mplshow takes a single command-line argument (either the filename or URL of a file created by mpltracker) and will load the figure(s) and show them in an interactive matplotlib window.

```
mplshow <file>.mpl
```

## Example

Below is a simple matplotlib figure created in the [simple example script](https://github.com/kecnry/mpltracker/blob/master/examples/simple.py) but which links to the output file from mpltracker.  Clicking on the image will show the `simple.mpl` file which could then be opened with mpltracker or mplshow from the command-line.

There is an [open issue](https://github.com/kecnry/mpltracker/issues/1) to support registering mplshow for specific file extensions or web-proticols so that clicking on an image linking to the .mpl file would automatically pop-up the interactive figure.  Until then, you need to copy the URL and call mplshow manually:

```
mplshow https://raw.githubusercontent.com/kecnry/mpltracker/master/examples/simple.mpl
```

<a href="https://raw.githubusercontent.com/kecnry/mpltracker/master/examples/simple.mpl"><img src="https://github.com/kecnry/mpltracker/blob/master/examples/simple.png" width="400px"/></a>

The html code for this is simply

```
<a href="https://raw.githubusercontent.com/kecnry/mpltracker/master/examples/simple.mpl"><img src="https://github.com/kecnry/mpltracker/blob/master/examples/simple.png" width="400px"/></a>
```

making it trivial to display images on a website which are then interactive (for any user that has mpltracker/mplshow installed) locally with a single click (once the [open issue](https://github.com/kecnry/mpltracker/issues/1) is close).

## How it works

mpltracker adds a decorator to all functions and methods inside the matplotlib module.  Whenever you make a call that goes through matplotlib, a lightweight wrapper is called first (either `intercept_func` or `intercept_method` in [mpltracker.py](https://github.com/kecnry/mpltracker/blob/master/mpltracker/mpltracker.py)) which gets the parent object (eg. fig or ax) or module (eg. plt), the name of the method or function you are trying to call, and all arguments (args) and keyword-arguments (kwargs).  The tracker object itself then records these items and passes along all the arguments to the originally requested call.  It then attaches the same decorators to any returned objects (eg. if you call ax=fig.add_subplot(111), mpltracker will now also intercept any calls to ax.\*), and gives that object an internal id so that when rebuilding the calls we know which resulting object to use.

Calling mpltracker.save simply dumps a json-formatted file of these stored arguments - just a list of dictionaries.  If you look at the [output file](https://github.com/kecnry/mpltracker/blob/master/examples/subplots.mpl) of subplots.py and compare it to the [subplots.py script](https://github.com/kecnry/mpltracker/blob/master/examples/subplots.py), you can see what is being stored.

The first call to matplotlib after tracking is enabled is `fig = plt.figure(figsize=(12,6))` which is then stored in the output file as:

```
{"returns": ["<id:140521903846288>"], "args": [], "obj": null, "func": "figure", "kwargs": {"figsize": [12, 6]}}
```

When rebuilding the figure, this simply says to call the `figure` function of `plt` (since obj is null) with no args and figsize=[12,6] as keyword arguments.  This will then return a single object (which was called fig in the script), and which is labeled with a random ID for later reference.

The second call to matplotlib is `ax1 = fig.add_subplot(121)` and is stored in the output file as:

```
{"returns": ["<id:140521903401296>"], "args": [121], "obj": "<id:140521903846288>", "func": "add_subplot", "kwargs": {}}
```

So as the second step of rebuilding the figure, this says to call the `add_subplot` *method* of whatever object was assigned to the ID associated with obj (in this case what we called fig), with [121] as args and no keyword arguments.  This in turn will return a single object (ax1) which will also be assigned ID.

## Credits

Much of the backbone behind mpltracker depends on hacking and decorating the matplotlib module.  Although slightly modified, most of the [modulehacker.py](https://github.com/kecnry/mpltracker/blob/master/mpltracker/modulehacker.py) and [decorations.py](https://github.com/kecnry/mpltracker/blob/master/mpltracker/decorations.py) were originally created by [Eric Snow](http://code.activestate.com/recipes/users/4177816/) and included here under the MIT license.  The originally postings can be found here for [modulehacker.py](http://code.activestate.com/recipes/577740/) and for [decorations.py](http://code.activestate.com/recipes/577742-apply-decorators-to-all-functions-in-a-module/) (these links can also be found in the credits in the source-code in this project).


## Contributing

Contributions are welcome!  Feel free to file an issue or fork and create a pull-request.
