#  import mpltracker BEFORE matplotlib
import mpltracker
import matplotlib.pyplot as plt

# start the tracker
mpltracker.start()

# make several comands to matplotlib
plt.plot([1,2,3],[1,2,3])
plt.title('my title')
plt.xlabel('my xlabel')

print mpltracker.list_commands()

# save the tracker to a file
mpltracker.save('simple.mpl')
mpltracker.stop()

# clear matplotlibs figure, just to show that there is no funny business
plt.clf()

# load the tracker from file and show the interactive matplotlib figure
mpltracker.show('simple.mpl')
