# Retention Cohort

import numpy as np
from scipy import interpolate
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import bokeh.plotting
from bokeh.models.renderers import figure, output_file, show
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

daily_organic_users = 100
arpdau = 0.10

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

#plt.plot(xdata, ydata, 'o')
#plt.ylabel('Retention')
#plt.xlabel('days since install')
#plt.plot(xnew, f(xnew))
#plt.show()

retention_column = pd.DataFrame(f(xnew), index=range(1, google_range + 1))
retention_curve = retention_column.T
retention_curve.index.name = 'days'

retention_days = pd.date_range(google_start, google_end).tolist()
retention_days = pd.DataFrame(retention_days)
retention_days.columns = ['date']
retention_days = retention_days.reset_index(drop=True)

dfs = [retention_days, retention_curve]
retention_cohort = pd.concat(dfs, axis=1)
retention_cohort = retention_cohort.set_index(['date'])

val = retention_cohort.values
i, j = np.triu_indices(val.shape[1])
val[i, j] = val[0][j - i]

users_cohort = retention_cohort.select_dtypes(exclude=['datetime']) * daily_organic_users
arpdau_cohort = users_cohort.select_dtypes(exclude=['datetime']) * arpdau
cumulative_retention = retention_cohort.sum()
LTV = cumulative_retention[google_range] * arpdau

retention_curve.iloc[0:1, 0:].T

LTV_table = pd.DataFrame(cumulative_retention)
LTV_table.columns = ['cum_retention']
LTV_table['LTV'] = LTV_table['cum_retention'] * arpdau
LTV_table['total_users'] = users_cohort.sum()
LTV_table['daily_revenue'] = LTV_table['total_users'] * arpdau
LTV_table['cum_revenue'] = LTV_table['daily_revenue'].cumsum()
LTV_table['retention_curve'] = retention_column
LTV_table = LTV_table.set_index(retention_days['date'])

LTV_table

#retention plot
plt.plot(LTV_table['retention_curve'], LTV_table['date'], 'o')
plt.ylabel('Retention')
plt.xlabel('days since install')
plt.show()

#output to Google Sheets
fiscal_calendar = Spread('calculator', 'fiscal_calendar')
fiscal_calendar.df_to_sheet(retention_cohort, sheet='retention')
fiscal_calendar.df_to_sheet(users_cohort, sheet='users')
fiscal_calendar.df_to_sheet(LTV_table, sheet='LTV')
fiscal_calendar.df_to_sheet(arpdau_cohort, sheet='revenue')


