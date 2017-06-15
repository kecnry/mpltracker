#  import mpltracker BEFORE matplotlib
import mpltracker
import matplotlib.pyplot as plt

# start the tracker
mpltracker.start()

# make several comands to matplotlib
fig = plt.figure(figsize=(12,6))
ax1 = fig.add_subplot(121)
ax2 = fig.add_subplot(122)
ax1.plot([1,2,3],[1,2,3])
ax1.set_title('ax1 title')
ax2.plot([4,5,6],[6,5,4])
ax2.set_title('ax2 title')

# save the tracker to a file
mpltracker.save('subplots.mpl')

# close matplotlibs figure, just to show that there is no funny business
# and so that both don't popup on plt.show()
plt.close(fig)

# load the tracker from file and show the interactive matplotlib figure
mpltracker.show('subplots.mpl')
