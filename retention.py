# LTV Table

import numpy as np
from scipy import interpolate
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from gspread_pandas import Spread

#inputs

ret_day_0 = 1.0
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

#function

def ltv_simple(ret_day_0, ret_day_1, ret_day_3, ret_day_7, ret_day_14, ret_day_30, ret_day_60, ret_day_90, ret_day_180, ret_day_365,
			   daily_organic_users, google_start_date, google_end_date):

	#reformat string dates to datetime
	year, month, day = map(int, google_start_date.split('-'))
	google_start = datetime.date(year, month, day)
	year, month, day = map(int, google_end_date.split('-'))
	google_end = datetime.date(year, month, day)

	#calculate range
	google_range = google_end - google_start
	google_range = google_range.days + 1

	#create arrays to get retention curve based on the user inputs
	xdata = np.array([0, 1, 3, 7, 14, 30, 60, 90, 180, 365])
	ydata = np.array([ret_day_0, ret_day_1, ret_day_3, ret_day_7, ret_day_14, ret_day_30, ret_day_60, ret_day_90, ret_day_180, ret_day_365])

	#create retention curve
	f = interpolate.interp1d(xdata, ydata)
	xnew = np.linspace(xdata[0], xdata[-1], google_range)

	#use retention curve to create dataframe table
	retention_column = pd.DataFrame(f(xnew), index=range(1, google_range + 1))
	retention_curve = retention_column.T
	retention_curve.index.name = 'days'

	#create retention date range based on the user input
	retention_days = pd.date_range(google_start, google_end).tolist()
	retention_days = pd.DataFrame(retention_days)
	retention_days.columns = ['date']
	retention_days = retention_days.reset_index(drop=True)

	#merge retention dates with retention values
	dfs = [retention_days, retention_curve]
	retention_cohort = pd.concat(dfs, axis=1)
	retention_cohort = retention_cohort.set_index(['date'])

	#shift rows by one column for each new row
	val = retention_cohort.values
	i, j = np.triu_indices(val.shape[1])
	val[i, j] = val[0][j - i]

	users_cohort = retention_cohort.select_dtypes(exclude=['datetime']) * daily_organic_users
	arpdau_cohort = users_cohort.select_dtypes(exclude=['datetime']) * arpdau
	cumulative_retention = retention_cohort.sum()
	#LTV = cumulative_retention[google_range] * arpdau not used at the moment

	LTV_table = pd.DataFrame(cumulative_retention)
	LTV_table.columns = ['cum_retention']
	LTV_table['LTV'] = LTV_table['cum_retention'] * arpdau
	LTV_table['daily_users'] = users_cohort.sum()
	LTV_table['total_users'] = LTV_table['daily_users'].cumsum()
	LTV_table['daily_revenue'] = LTV_table['daily_users'] * arpdau
	LTV_table['cum_revenue'] = LTV_table['daily_revenue'].cumsum()
	LTV_table['retention_curve'] = retention_column
	LTV_table = LTV_table.set_index(retention_days['date'])

	# retention plot

	plt.plot(xnew, retention_column, '-.')
	plt.ylabel('Retention')
	plt.xlabel('days since install')
	retention_plot = plt.show()

	# users plot

	plt.plot(xnew, LTV_table['daily_users'], '-.')
	plt.ylabel('Cumulative Revenue')
	plt.xlabel('days since install')
	users_plot = plt.show()

	# revenue plot

	plt.plot(xnew, LTV_table['cum_revenue'], '-.')
	plt.ylabel('Cumulative Revenue')
	plt.xlabel('days since install')
	revenue_plot = plt.show()

	return LTV_table, retention_plot, users_plot, revenue_plot

#check
ltv_simple(ret_day_0, ret_day_1, ret_day_3, ret_day_7, ret_day_14, ret_day_30, ret_day_60, ret_day_90,
				  ret_day_180, ret_day_365, daily_organic_users, google_start_date, google_end_date)


#output to Google Sheets to check
fiscal_calendar = Spread('calculator', 'fiscal_calendar')
fiscal_calendar.df_to_sheet(retention_cohort, sheet='retention')
fiscal_calendar.df_to_sheet(users_cohort, sheet='users')
fiscal_calendar.df_to_sheet(LTV_table, sheet='LTV')
fiscal_calendar.df_to_sheet(arpdau_cohort, sheet='revenue')


