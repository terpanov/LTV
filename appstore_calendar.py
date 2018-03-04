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

# Apple Calendar

def apple_calendar(date_entry, revenue):
	apple_fiscal = pd.read_csv(csv_path, parse_dates=True, index_col=None)
	apple_fiscal['date'] = pd.to_datetime(apple_fiscal['date'])  # convert date object to datetime
	apple_date = apple_fiscal['date'].to_frame()
	apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])  # convert date object to datetime
	apple_starts = apple_fiscal[['start_date', 'date']]  # assign start dates to datetime
	apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
	apple_ends = apple_fiscal[['end_date', 'date']]
	apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
	apple_pays = apple_fiscal['pay_date']

	apple_duration = apple_fiscal[['date', 'next_month_duration']]
	#apple_fiscal['payment_start'] = pd.to_datetime(apple_fiscal['payment_start'])
	#payment_start = apple_fiscal[['payment_start', 'date']]
	#apple_fiscal['payment_end'] = pd.to_datetime(apple_fiscal['payment_end'])
	#payment_end = apple_fiscal[['payment_end', 'date']]

	year, month, day = map(int, date_entry.split('-'))  # set parse format
	sample_date = datetime.date(year, month, day)  # parse date entry string
	start_datelist = pd.date_range(sample_date, periods=365).tolist()  # create list of annual dates
	start_apple_table = pd.DataFrame(start_datelist)  # convert list to data frame
	start_apple_table.index.name = 'days'  # name index 'days'
	start_apple_table.columns = ['date']  # name dates column 'date'

	start_apple_table = start_apple_table.merge(apple_starts, how='left', on='date', left_index=True)
	start_apple_table = start_apple_table.merge(apple_ends, how='left', on='date', left_index=True)

	#start_apple_table = start_apple_table.merge(payment_start, how='left', on='date', left_index=True)
	#start_apple_table = start_apple_table.merge(payment_end, how='left', on='date', left_index=True)
	start_apple_table = start_apple_table.merge(apple_duration, how='left', on='date', left_index=True)

	start_apple_table['date'] = start_apple_table.loc[(start_apple_table['date'].isin(apple_pays)), 'pay_date'] \
		= start_apple_table['date']

	start_apple_table['sample_sales'] = revenue
	start_apple_table = start_apple_table.set_index('date')

	start_apple_table['next_month_duration'] = pd.to_timedelta(start_apple_table['next_month_duration'], unit='D')

	start_apple_table['monthly_sales'] = start_apple_table.apply(
		lambda x: start_apple_table.loc[
			(start_apple_table['start_date'] <= x.name) & (x.name <= start_apple_table['end_date']),
			['sample_sales']].sum(), axis=1)

	start_apple_table['monthly_adj'] = start_apple_table.apply(
		lambda x: start_apple_table.loc[(start_apple_table['start_date']
										 + start_apple_table['next_month_duration'] <= x.name) & (
												x.name <= start_apple_table['end_date'] +
												start_apple_table['next_month_duration']), ['sample_sales']].sum(),
		axis=1)

	start_apple_table['monthly_shift'] = start_apple_table['monthly_adj'].shift(7)

	start_apple_table['monthly_payment'] = start_apple_table['monthly_shift'].loc[start_apple_table['pay_date'].notnull()]

	return start_apple_table

# Google Calendar

def google_calendar(date_entry, revenue):
	year, month, day = map(int, date_entry.split('-'))							# set parse format
	sample_date = datetime.date(year, month, day)								# parse date entry string
	start_datelist = pd.date_range(sample_date, periods=365).tolist()			# create list of annual dates
	start_google_table = pd.DataFrame(start_datelist)							# convert list to dataframe
	start_google_table.index.name = 'days'										# name index 'days'
	start_google_table.columns = ['date']										# name dates column 'date'
	start_google_table.loc[(start_google_table['date'].dt.day == 1), 'start_date'] = \
		start_google_table['date']												# create start date column
	start_google_table['start_date'] = start_google_table['start_date'].fillna(method='ffill')
	start_google_table['date'] = start_google_table.loc[start_google_table['date'].dt.is_month_end,  # end date column
		'end_date'] = start_google_table['date']
	start_google_table['end_date'] = start_google_table['end_date'].fillna(method='bfill')
	start_google_table.loc[(start_google_table['date'].dt.day == 15), 'pay_date'] = \
		start_google_table['date']
	start_google_table.loc[(start_google_table['date'].dt.day == 15), 'pay_period'] = \
		start_google_table['date'] - pd.DateOffset(months=1)								# create pay date column
	start_google_table['sample_sales'] = revenue
	start_google_table = start_google_table.set_index('date')
	start_google_table['monthly_payment'] = \
		start_google_table.apply(lambda x: start_google_table.loc[(start_google_table['start_date'] +
		pd.DateOffset(months=1) <= x.name)
		& (x.name <= start_google_table['end_date'] + pd.DateOffset(months=1)), ['sample_sales']].sum(), axis=1)
	start_google_table['monthly_payment'] = start_google_table['monthly_payment'].loc[start_google_table['pay_period'].notnull()]
	return start_google_table


# Check if calendars are workings
revenue = list(range(1, 366))

print(apple_calendar('2017-11-05', revenue))
print(google_calendar('2017-11-01', revenue))




apple_sum = apple_calendar('2017-11-05')
type(apple_sum)
apple_sum['monthly_payment'].sum()
apple_sum.describe()

google_sum = google_calendar('2017-11-01')
type(google_sum)
google_sum['monthly_payment'].sum()
google_sum.describe()


# Google Pay Date

def google_paydate(date_entry):
	year , month , day = map(int , date_entry.split('-'))						# set parse format
	sample_date = datetime.date(year , month , day)								# parse date entry string
	sample_date = datetime.date(sample_date.year, sample_date.month,			# find last day of the month
									calendar.monthrange(sample_date.year , sample_date.month)[ -1 ])
	return sample_date + datetime.timedelta(days=15)							# last day of the month + 15 days

# Apple Pay Date

def apple_paydate(date_entry):
	apple_fiscal = pd.read_csv(csv_path, parse_dates=True , index_col=None)
	apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date']) 	# convert date object to datatime
	apple_start_date = apple_fiscal['start_date']								# assign to datatime
	apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
	apple_end_date = apple_fiscal['end_date']
	apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
	apple_pay_date = apple_fiscal['pay_date']
	year, month, day = map(int, date_entry.split('-'))							# set parse format
	sample_date = datetime.date(year, month, day)								# parse date entry string
	mask = (sample_date > apple_start_date) & (sample_date <= apple_end_date)	# tuple for payment period
	apple_pay = pd.to_datetime(apple_pay_date.loc[mask].values[0], format='%Y-%m-%d').date() #find apple pay date
	return apple_pay

# Check if pay dates are workings

print(apple_paydate('2017-11-01'))
print(google_paydate('2017-11-01'))

# Output to Google Sheets to check

apple_fiscal = apple_calendar('2017-11-01', revenue)
fiscal_calendar = Spread('calculator', 'fiscal_calendar')
fiscal_calendar.df_to_sheet(apple_fiscal, sheet='apple_output')
print(fiscal_calendar)

google_fiscal = google_calendar('2017-11-01', revenue)
fiscal_calendar.df_to_sheet(google_fiscal, sheet='google_output')
print(fiscal_calendar)



