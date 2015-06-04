#!/usr/bin/python

## dependencies:
##   - matplotlib 1.2+

import sys
import pickle
import matplotlib.pyplot as plt
import urllib2

url = sys.argv[1].lstrip("mpl://")
#url = "http://127.0.0.1:8000/static/test.mpl.pickle"

data = urllib2.urlopen(url)
# TODO: handle security https://docs.python.org/3.4/library/pickle.html#restricting-globals
# TODO: gui with option to show fig or open python terminal with fig loaded
mplfig = pickle.load(data)
plt.show()
