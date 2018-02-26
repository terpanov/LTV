"""Apple and Google Payment Calendars
Apple pulls calendar from Google Sheets
Google is a pure function"""

import pandas as pd
from gspread_pandas import Spread
import datetime
import calendar

# Apple Calendar

fiscal_calendar = Spread('LTV', 'fiscal_calendar')
fiscal_calendar.open_sheet(0)

apple_fiscal = fiscal_calendar.sheet_to_df(header_rows=1, index=False)
apple_fiscal.head()

apple_fiscal['fiscal_months'] = pd.to_datetime(apple_fiscal['fiscal_month'])
fiscal_months = apple_fiscal['fiscal_months']

apple_fiscal['start_date'] = pd.to_datetime(apple_fiscal['start_date'])
start_date = apple_fiscal['start_date']

apple_fiscal['end_date'] = pd.to_datetime(apple_fiscal['end_date'])
end_date = apple_fiscal['end_date']

apple_fiscal['pay_date'] = pd.to_datetime(apple_fiscal['pay_date'])
pay_date = apple_fiscal['pay_date']

def apple_paydate():
    date_entry = input('Enter Apple app store start date in YYYY-MM-DD format')
    year , month , day = map(int , date_entry.split ('-'))
    sample_date = datetime.date(year , month , day)
    mask = (sample_date > start_date) & (sample_date <= end_date)
    apple_pay = pd.to_datetime(pay_date.loc[mask].values[0], format='%Y-%m-%d', errors='coerce').date()
    return apple_pay

# Google Calendar

def google_paydate():
    date_entry = input('Enter Google Play store date in YYYY-MM-DD format')
    year , month , day = map(int , date_entry.split('-'))
    sample_date = datetime.date(year , month , day)
    sample_date = datetime.date(sample_date.year , sample_date.month ,
                                    calendar.monthrange(sample_date.year , sample_date.month)[ -1 ])
    return sample_date + datetime.timedelta(days=15)

# Check

print(apple_paydate())
print(google_paydate())







