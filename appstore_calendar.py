"""Apple and Google Payment Calendars
Apple pulls calendar from Google Sheets
Google is a pure function
payment outputs the next payment date from the app stores
calendar outputs annual table with period start, end and pay dates"""

import pandas as pd
import datetime
import calendar
import os
from gspread_pandas import Spread
import numpy as np

# Path to CSV file

file_path = os.path.abspath('apple_fiscal_calendar_2018_2021.csv')
print(file_path)
dir_path = os.path.dirname(file_path)
print(dir_path)
csv_path = os.path.join(dir_path, 'apple_fiscal_calendar_2018_2021.csv')

# Apple Calendar, uses date_entry - first date, revenue - list of daily sales

def apple_calendar(date_entry, revenue):
	apple_fiscal = pd.read_csv(csv_path, parse_dates=True, index_col=None)

	# convert date, start and end date range, pay date and month duration to datetime
	apple_fiscal['date'] = pd.to_datetime(apple_fiscal['date'])
	apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])
	apple_starts = apple_fiscal[['start_date', 'date']]
	apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
	apple_ends = apple_fiscal[['end_date', 'date']]
	apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
	apple_pays = apple_fiscal['pay_date']
	apple_duration = apple_fiscal[['date', 'next_month_duration']]

	# set parse format / parse date entry string
	year, month, day = map(int, date_entry.split('-'))
	sample_date = datetime.date(year, month, day)

	# create list of annual dates, based on the start date from date entry variable and convert list to data frame
	start_datelist = pd.date_range(sample_date, periods=365).tolist()
	start_apple_table = pd.DataFrame(start_datelist)

	# name index 'days' and column 'date'
	start_apple_table.index.name = 'days'
	start_apple_table.columns = ['date']

	# merge csv columns 'start_date', 'end_date', and 'next_month_duration' with data frame
	start_apple_table = start_apple_table.merge(apple_starts, how='left', on='date', left_index=True)
	start_apple_table = start_apple_table.merge(apple_ends, how='left', on='date', left_index=True)
	start_apple_table = start_apple_table.merge(apple_duration, how='left', on='date', left_index=True)

	# add 'pay_date' column to list only the days when receive payment from Apple
	start_apple_table['date'] = start_apple_table.loc[(start_apple_table['date'].isin(apple_pays)), 'pay_date'] \
		= start_apple_table['date']

	# assign 'sample_sales' column to second input revenue
	start_apple_table['sample_sales'] = revenue

	# change index to column 'date'
	start_apple_table = start_apple_table.set_index('date')

	# convert 'next_month_duration' from integer to datetime days
	start_apple_table['next_month_duration'] = pd.to_timedelta(start_apple_table['next_month_duration'], unit='D')

	# create 'monthly_sales' column
	start_apple_table['monthly_sales'] = start_apple_table.apply(lambda x: start_apple_table.loc[(start_apple_table['start_date']
		<= x.name) & (x.name <= start_apple_table['end_date']), ['sample_sales']].sum(), axis=1)

	# create 'monthly_adj' column to move the sales up by next month fiscal duration period
	start_apple_table['monthly_adj'] = start_apple_table.apply(lambda x: start_apple_table.loc[(start_apple_table['start_date']
		+ start_apple_table['next_month_duration'] <= x.name) & (x.name <= start_apple_table['end_date'] +
		start_apple_table['next_month_duration']), ['sample_sales']].sum(), axis=1)

	# shift 'monthly_adj' by 7 rows to be captured by 'pay_date'
	start_apple_table['monthly_shift'] = start_apple_table['monthly_adj'].shift(7)

	# add 'monthly_payment' and show only on 'pay_date' dates
	start_apple_table['monthly_payment'] = start_apple_table['monthly_shift'].loc[start_apple_table['pay_date'].notnull()]

	# add 'cumulative_payment' column
	start_apple_table['cumulative_payment'] = start_apple_table['monthly_payment'].cumsum()

	return start_apple_table

# Google Calendar, uses date_entry - first date, revenue - list of daily sales

def google_calendar(date_entry, revenue):
	# set parse format and parse date entry string
	year, month, day = map(int, date_entry.split('-'))
	sample_date = datetime.date(year, month, day)

	# create list of annual dates and convert list to data frame
	start_datelist = pd.date_range(sample_date, periods=365).tolist()
	start_google_table = pd.DataFrame(start_datelist)

	# name index 'days' and column 'date'
	start_google_table.index.name = 'days'
	start_google_table.columns = ['date']

	# create 'start_date', 'end_date' columns, and use front and back fill
	start_google_table.loc[(start_google_table['date'].dt.day == 1), 'start_date'] = start_google_table['date']
	start_google_table['start_date'] = start_google_table['start_date'].fillna(method='ffill')
	start_google_table['date'] = start_google_table.loc[start_google_table['date'].dt.is_month_end, 'end_date'] = start_google_table['date']
	start_google_table['end_date'] = start_google_table['end_date'].fillna(method='bfill')

	# create 'pay_date' and 'pay_period' columns
	start_google_table.loc[(start_google_table['date'].dt.day == 15), 'pay_date'] = start_google_table['date']
	start_google_table.loc[(start_google_table['date'].dt.day == 15), 'pay_period'] = start_google_table['date'] - pd.DateOffset(months=1)

	# assign 'sample_sales' column to second input revenue
	start_google_table['sample_sales'] = revenue

	# change index to column 'date'
	start_google_table = start_google_table.set_index('date')

	# add 'monthly_payment', set it to only when 'pay_period' is on and then add 'cumulative_payment' column
	start_google_table['monthly_payment'] = start_google_table.apply(lambda x: start_google_table.loc[(start_google_table['start_date'] +
		pd.DateOffset(months=1) <= x.name) & (x.name <= start_google_table['end_date'] + pd.DateOffset(months=1)), ['sample_sales']].sum(), axis=1)
	start_google_table['monthly_payment'] = start_google_table['monthly_payment'].loc[start_google_table['pay_period'].notnull()]
	start_google_table['cumulative_payment'] = start_google_table['monthly_payment'].cumsum()
	return start_google_table


# add revenue variable and Apple and Google start dates to run calendars
revenue = list(range(1, 366))
apple_start_date = '2017-11-01'
google_start_date = '2017-11-01'

# simple check to see if calendars are workings
print(apple_calendar(apple_start_date, revenue))
print(google_calendar(google_start_date, revenue))

# test calendars
apple_sum = apple_calendar(apple_start_date, revenue)
type(apple_sum)
apple_sum['monthly_payment'].sum()
apple_sum.describe()

google_sum = google_calendar(google_start_date, revenue)
type(google_sum)
google_sum['monthly_payment'].sum()
google_sum.describe()

# Output to Google Sheets, using gspread to check in more detail
apple_fiscal = apple_calendar(apple_start_date, revenue)
fiscal_calendar = Spread('calculator', 'fiscal_calendar')
fiscal_calendar.df_to_sheet(apple_fiscal, sheet='apple_output')
print(fiscal_calendar)

google_fiscal = google_calendar(google_start_date, revenue)
fiscal_calendar.df_to_sheet(google_fiscal, sheet='google_output')
print(fiscal_calendar)




