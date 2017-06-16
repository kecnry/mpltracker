import mpltracker
import matplotlib.pyplot as plt

# you must call mpltracker.figure instead of plt.figure if you want the
# tracker attached to just that figure (ie. you cannot track a single
# object retroactively)
fig1 = mpltracker.figure()
fig2 = mpltracker.figure(figsize=(12,6))

# now any command that acts on fig1 OR its children (ie fig1ax) will be
# in its own tracker instance
fig1ax = fig1.add_subplot(111)
fig1ax.plot([1,2,3],[1,2,3], color='blue')
fig1ax.set_title('figure 1')

# even when calling functions from the top-level of the matplotlib module,
# mpltracker will recognize that its acting on the figure and save those
# commands in the appropriate tracker
fig2ax = fig2.add_subplot(111)
plt.plot([1,2,3],[3,2,1], color='red')
plt.title('figure 2')

# in addition to figure, axes is also supported.
ax = mpltracker.axes()
ax.plot([1,2,3], [1,2,3], color='k', linestyle='dashed')
plt.title('axes')

# to get the tracker for a specific object, just pass that object (figure or axes)
# to mpltracker.gct()
mpltracker.gct(fig1).save('multiple_trackers_fig1.mpl')
mpltracker.gct(fig2).save('multiple_trackers_fig2.mpl')
mpltracker.gct(ax).save('multiple_trackers_ax.mpl')

plt.close(fig1)
plt.close(fig2)
plt.cla()

# NOTE: because there is no way to close an axes instance, this first call
# will likely also popup and empty figure.  If running the rest of this script
# from a new python instance, that would not happen
mpltracker.show('multiple_trackers_fig1.mpl')
mpltracker.show('multiple_trackers_fig2.mpl')
mpltracker.show('multiple_trackers_ax.mpl')
