"""Apple and Google Payment Calendars
Apple pulls calendar from Google Sheets
Google is a pure function
Calendar outputs the next payment date from the app stores"""

import pandas as pd
from gspread_pandas import Spread
import datetime
import calendar


# Get Apple start and end dates for entry date

fiscal_calendar = Spread('LTV', 'fiscal_calendar')
fiscal_calendar.open_sheet(0)

apple_fiscal = fiscal_calendar.sheet_to_df(header_rows=1, index=False)
apple_fiscal.head()

apple_fiscal['fiscal_months'] = pd.to_datetime(apple_fiscal['fiscal_month'])
fiscal_months = apple_fiscal['fiscal_months']

apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])
apple_start_date = apple_fiscal['start_date']

apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
apple_end_date = apple_fiscal['end_date']

apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
apple_pay_date = apple_fiscal['pay_date']

# Apple Calendar

def apple_paydate():
    date_entry = input('Enter Apple app store start date in YYYY-MM-DD format')
    year , month , day = map(int , date_entry.split ('-'))
    sample_date = datetime.date(year , month , day)
    mask = (sample_date > apple_start_date) & (sample_date <= apple_end_date)
    apple_pay = pd.to_datetime(apple_pay_date.loc[mask].values[0], format='%Y-%m-%d', errors='coerce').date()
    return apple_pay

# Google Calendar

def google_paydate():
    date_entry = input('Enter Google Play store date in YYYY-MM-DD format')
    year , month , day = map(int , date_entry.split('-'))
    sample_date = datetime.date(year , month , day)
    sample_date = datetime.date(sample_date.year , sample_date.month ,
                                    calendar.monthrange(sample_date.year , sample_date.month)[ -1 ])
    return sample_date + datetime.timedelta(days=15)

# Get Google start and end dates for entry date

date_entry = '2018-10-10'
year , month , day = map (int , date_entry.split ('-'))
sample_date = datetime.date (year , month , day)
google_start_date = datetime.date(sample_date.year , sample_date.month , 1)
_, num_days = calendar.monthrange(sample_date.year , sample_date.month)
google_end_date = datetime.date(sample_date.year , sample_date.month , num_days)

print(google_start_date)
print(google_end_date)

# Check if pay dates are workings

print(apple_paydate())
print(google_paydate())







