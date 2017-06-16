#  import mpltracker BEFORE matplotlib
import mpltracker
import matplotlib.pyplot as plt

# start the tracker
mpltracker.start()

# make several comands to matplotlib
plt.plot([1,2,3],[1,2,3])
plt.title('my title')
plt.xlabel('my xlabel')

# save the tracker to a file
mpltracker.save('simple.mpl')

# also save the image itself to a png
plt.savefig('simple.png')

# clear matplotlibs figure, just to show that there is no funny business
plt.clf()

# load the tracker from file and show the interactive matplotlib figure
mpltracker.show('simple.mpl')
