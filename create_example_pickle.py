import matplotlib.pyplot as plt
import pickle

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot([1,2,3],[1,2,3])

f = open('test.mpl.pickle', 'wb')
pickle.dump(fig, f)
f.close()
