"""Apple and Google Payment Calendars
Apple pulls calendar from Google Sheets
Google is a pure function
Calendar outputs the next payment date from the app stores"""

import pandas as pd
import datetime
import calendar

# Apple Calendar

def apple_paydate(date_entry):
    apple_fiscal = pd.read_csv ('/Users/plexchat/LTV_Geek/LTV_Files/apple_fiscal_calendar_2018_2021.csv' ,
                                parse_dates=True , index_col=None)
    apple_fiscal[ 'start_date' ] = pd.to_datetime (apple_fiscal[ 'start_date' ])
    apple_start_date = apple_fiscal[ 'start_date' ]
    apple_fiscal[ 'end_date' ] = pd.to_datetime (apple_fiscal[ 'end_date' ])
    apple_end_date = apple_fiscal[ 'end_date' ]
    apple_fiscal[ 'pay_date' ] = pd.to_datetime (apple_fiscal[ 'pay_date' ])
    apple_pay_date = apple_fiscal[ 'pay_date' ]
    year , month , day = map(int , date_entry.split ('-'))
    sample_date = datetime.date(year , month , day)
    mask = (sample_date > apple_start_date) & (sample_date <= apple_end_date)
    apple_pay = pd.to_datetime(apple_pay_date.loc[mask].values[0], format='%Y-%m-%d', errors='coerce').date()
    return apple_pay, apple_start_date[0].date(), apple_end_date[0].date()

# Google Calendar

def google_paydate(date_entry):
    year , month , day = map(int , date_entry.split('-'))
    sample_date = datetime.date(year , month , day)
    sample_date = datetime.date(sample_date.year , sample_date.month ,
                                    calendar.monthrange(sample_date.year , sample_date.month)[ -1 ])
    google_start_date = datetime.date (sample_date.year , sample_date.month , 1)
    _ , num_days = calendar.monthrange (sample_date.year , sample_date.month)
    google_end_date = datetime.date (sample_date.year , sample_date.month , num_days)
    return sample_date + datetime.timedelta(days=15), google_start_date, google_end_date


# Check if pay dates are workings

print(apple_paydate('2018-10-10'))
print(google_paydate('2018-10-10'))







