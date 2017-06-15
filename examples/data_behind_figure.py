#  import mpltracker BEFORE matplotlib
import mpltracker
import matplotlib.pyplot as plt

# start the tracker
mpltracker.start()

# make several comands to matplotlib
plt.plot([1,2,3],[1,2,3])

# access the data from the mpltracker module directly
print("get_data:")
print(mpltracker.get_data())

print("get_data_table:")
print(mpltracker.get_data_table())

# dump the data table to a file ready to send to journals
mpltracker.write_data_table(filename='data_behind_figure.ecsv')

# this data is also all accessible after saving the tracker to disk
mpltracker.save('data_behind_figure.mpl')

print("from saved file get_data:")
print mpltracker.get_data('data_behind_figure.mpl')

print("from saved file get_data:")
print mpltracker.get_data_table('data_behind_figure.mpl')
