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
* [astropy (optional - used for exporting to tables](https://github.com/astropy/astropy)

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

## Credits

Much of the backbone behind mpltracker depends on hacking and decorating the matplotlib module.  Although slightly modified, most of the [modulehacker.py](https://github.com/kecnry/mpltracker/blob/master/mpltracker/modulehacker.py) and [decorations.py](https://github.com/kecnry/mpltracker/blob/master/mpltracker/decorations.py) were originally created by [Eric Snow](http://code.activestate.com/recipes/users/4177816/) and included here under the MIT license.  The originally postings can be found here for [modulehacker.py](http://code.activestate.com/recipes/577740/) and for [decorations.py](http://code.activestate.com/recipes/577742-apply-decorators-to-all-functions-in-a-module/) (these links can also be found in the credits in the source-code in this project).


## Contributing

Contributions are welcome!  Feel free to file an issue or fork and create a pull-request.
