# Retention Cohort

import numpy as np
from scipy import interpolate
import pandas as pd
import matplotlib.pyplot as plt
from gspread_pandas import Spread

ret_day_1 = 0.6
ret_day_3 = 0.5
ret_day_7 = 0.4
ret_day_14 = 0.3
ret_day_30 = 0.2
ret_day_60 = 0.15
ret_day_90 = 0.10
ret_day_180 = 0.05
ret_day_365 = 0

google_start_date = '2017-12-10'
google_end_date = '2018-12-03'

year, month, day = map(int, google_start_date.split('-'))
google_start = datetime.date(year, month, day)
year, month, day = map(int, google_end_date.split('-'))
google_end = datetime.date(year, month, day)

google_range = google_end - google_start
google_range = google_range.days + 1

xdata = np.array([1, 3, 7, 14, 30, 60, 90, 180, 365])
ydata = np.array([ret_day_1, ret_day_3, ret_day_7, ret_day_14, ret_day_30, ret_day_60, ret_day_90, ret_day_180, ret_day_365])

f = interpolate.interp1d(xdata, ydata)
xnew = np.linspace(xdata[0], xdata[-1], google_range)

plt.plot(xdata, ydata, 'o')
plt.ylabel('Retention')
plt.xlabel('days since install')
plt.plot(xnew, f(xnew))
plt.show()

retention_curve = pd.DataFrame(f(xnew), index=range(1, google_range + 1))
retention_curve = retention_curve.T
retention_curve.index.name = 'days'

retention_days = pd.date_range(google_start, google_end).tolist()
retention_days = pd.DataFrame(retention_days)
retention_days.columns = ['date']
retention_days = retention_days.reset_index(drop=True)

dfs = [retention_days, retention_curve]
combined = pd.concat(dfs, axis=1)
combined = combined.set_index(['date'])

val = combined.values
i, j = np.triu_indices(val.shape[1])
val[i, j] = val[0][j - i]
combined


#output to Google Sheets
fiscal_calendar = Spread('calculator', 'fiscal_calendar')
fiscal_calendar.df_to_sheet(combined, sheet='retention')



