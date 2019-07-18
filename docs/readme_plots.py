import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('..')

import timpy as tplt

series = pd.Series([1,1,2,3,4], index=["2019-06-01", "2019-07-03", "2019-07-14", "2019-08-01", "2019-08-02"])
tplt.calendar(series)

plt.savefig("img/example_plot_1.png")