from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

options = Options()
options.add_argument("--headless")
#options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options)

# ryanair endpoints

# https://www.ryanair.com/api/views/locate/5/airports/it/active
# https://www.ryanair.com/api/booking/v4/it-it/availability?ADT=1&CHD=0&DateIn=2023-02-03&DateOut=2023-02-01&Destination=VLC&Disc=0&INF=0&Origin=TSF&TEEN=0&promoCode=&IncludeConnectingFlights=false&FlexDaysBeforeOut=2&FlexDaysOut=2&FlexDaysBeforeIn=2&FlexDaysIn=2&RoundTrip=true&ToUs=AGREED
# https://www.ryanair.com/api/views/locate/5/airports/it/TSF
# https://services-api.ryanair.com/farfnd/3/oneWayFares?&departureAirportIataCode=BCN&language=en&limit=16&market=en-gb&offset=0&outboundDepartureDateFrom=2023-02-11&outboundDepartureDateTo=2023-02-27&priceValueTo=150
# https://www.ryanair.com/api/farfnd/3/oneWayFares/ORIGIN_AIRPORT_CODE/DEST_AIRPORT_CODE/cheapestPerDay?outboundDateFrom=2020-02-01&outboundDateTo=2021-02-01
# https://api.ryanair.com/farefinder/3/roundTripFares?&arrivalAirportIataCode=STN&departureAirportIataCode=VLC&inboundDepartureDateFrom=2016-10-11&inboundDepartureDateTo=2017-10-28&language=es&limit=16&market=es-es&offset=0&outboundDepartureDateFrom=2016-10-11&outboundDepartureDateTo=2017-10-28&priceValueTo=150
def get_dates(month, year, separator="-"):
    # get the first day of the month
    first_day = datetime(year, month, 1)
    # get the last day of the month
    last_day = first_day + timedelta(days=31)
    last_day = last_day.replace(day=1) - timedelta(days=1)
    # get the number of days in the month
    days_in_month = (last_day - first_day).days + 1
    # if the month is the current month, we need to remove the past days
    if first_day.month == datetime.now().month and first_day.year == datetime.now().year:
        days_in_month = days_in_month - datetime.now().day + 1
        first_day = datetime.now()
    # get the dates of the month
    dates = [first_day + timedelta(days=i) for i in range(days_in_month)]
    # convert dates to string
    dates = [date.strftime("%d" + separator + "%m" + separator + "%Y") for date in dates]
    return dates



dates = get_dates(2, 2023, "-")
response = requests.get(f"https://www.ryanair.com/api/farfnd/3/oneWayFares/BCN/IBZ/cheapestPerDay?outboundDateFrom=2023-02-01&outboundDateTo=2023-02-28")
data = json.loads(response.text)

# Loop through each fare
for fare in data['outbound']['fares']:
    # Check if price is not null and fare is not unavailable or sold out
    if fare['price'] is not None and not fare['soldOut'] and not fare['unavailable']:
        day = fare['day']
        price = fare['price']['value']
        print(f"Day: {day}, Price: {price}")
