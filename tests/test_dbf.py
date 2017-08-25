from nose.tools import assert_raises

import mpltracker
import matplotlib.pyplot as plt

def test_dbf():
    mpltracker.start()


    plt.plot([1,2,3],[1,2,3])

    # for now, let's just make sure everything runs
    # TODO: add assertions
    mpltracker.get_data()
    mpltracker.get_data_table()

    mpltracker.write_data_table(filename='data_behind_figure.ecsv')

    mpltracker.save('data_behind_figure.mpl')

    mpltracker.get_data('data_behind_figure.mpl')
    mpltracker.get_data_table('data_behind_figure.mpl')

if __name__ == '__main__':
    test_dbf()
