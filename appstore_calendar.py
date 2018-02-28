"""Apple and Google Payment Calendars
Apple pulls calendar from Google Sheets
Google is a pure function
Calendar outputs the next payment date from the app stores"""

import pandas as pd
import datetime
import calendar
from pathlib import Path
DATA_DIR = Path('.')

# Apple Pay Date

def apple_paydate(date_entry):
	apple_fiscal = pd.read_csv('/Users/plexchat/LTV_Geek/LTV_Files/LTV/apple_fiscal_calendar_2018_2021.csv',
								parse_dates=True , index_col=None)
	apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])
	apple_start_date = apple_fiscal['start_date']
	apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
	apple_end_date = apple_fiscal['end_date']
	apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
	apple_pay_date = apple_fiscal['pay_date']
	year, month, day = map(int, date_entry.split('-'))
	sample_date = datetime.date(year, month, day)
	mask = (sample_date > apple_start_date) & (sample_date <= apple_end_date)
	apple_pay = pd.to_datetime(apple_pay_date.loc[mask].values[0], format='%Y-%m-%d').date()
	return apple_pay

print(apple_paydate('2018-10-10'))

# Apple Calendar

def apple_calendar(date_entry):
	apple_fiscal = pd.read_csv('/Users/plexchat/LTV_Geek/LTV_Files/LTV/apple_fiscal_calendar_2018_2021.csv',
							   parse_dates=True, index_col=None)
	apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])
	apple_starts = apple_fiscal['start_date']
	apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
	apple_ends = apple_fiscal['end_date']
	apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
	apple_pays = apple_fiscal['pay_date']
	year, month, day = map(int, date_entry.split('-'))
	sample_date = datetime.date(year, month, day)
	start_datelist = pd.date_range(sample_date, periods=365).tolist()
	start_apple_table = pd.DataFrame(start_datelist)
	start_apple_table.index.name = 'days'
	start_apple_table.columns = ['date']
	start_apple_table['date'] = start_apple_table.loc[(start_apple_table['date'].isin(apple_starts)), 'start_date'] \
		= start_apple_table['date']
	start_apple_table['date'] = start_apple_table.loc[(start_apple_table['date'].isin(apple_ends)), 'end_date'] \
		= start_apple_table['date']
	start_apple_table['date'] = start_apple_table.loc[(start_apple_table['date'].isin(apple_pays)), 'pay_date'] \
		= start_apple_table['date']
	return start_apple_table

 print(apple_calendar('2018-10-10'))

# Google Pay Date

def google_paydate(date_entry):
	year , month , day = map(int , date_entry.split('-'))
	sample_date = datetime.date(year , month , day)
	sample_date = datetime.date(sample_date.year, sample_date.month,
									calendar.monthrange(sample_date.year , sample_date.month)[ -1 ])
	return sample_date + datetime.timedelta(days=15)

# Google Calendar

def google_calendar(date_entry):
	year, month, day = map(int, date_entry.split('-'))
	sample_date = datetime.date(year, month, day)
	start_datelist = pd.date_range(sample_date, periods=365).tolist()
	start_google_table = pd.DataFrame(start_datelist)
	start_google_table.index.name = 'days'
	start_google_table.columns = ['date']
	start_google_table.loc[(start_google_table['date'].dt.day == 1), 'start_date'] = \
		start_google_table['date']
	start_google_table['date'] = start_google_table.loc[start_google_table['date'].dt.is_month_end,
														'end_date'] = start_google_table['date']
	start_google_table.loc[(start_google_table['date'].dt.day == 15), 'pay_date'] = \
		start_google_table['date']
	return start_google_table


# Check if pay dates are workings

print(apple_paydate('2018-10-10'))
print(google_paydate('2018-10-10'))

# Check if calendars are workings

print(google_calendar('2018-10-10'))
print(apple_calendar('2018-10-10'))

