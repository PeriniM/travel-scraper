import json
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_city_legacy_id(city_name):
    response = requests.get(f"https://global.api.flixbus.com/search/autocomplete/cities?q={city_name}")
    data = json.loads(response.text)
    best_match = max(data, key=lambda x: x["score"])
    return best_match["legacy_id"]

def get_dates(month, year, separator=".", log=False):
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
    if log:
        print(f"dates: {dates}")
    return dates

def get_price_duration(departureCity, arrivalCity, departureDate, driver, log=False):
    id_departure = get_city_legacy_id(departureCity)
    id_arrival = get_city_legacy_id(arrivalCity)
    driver.get(f"https://shop.flixbus.it/search?_locale=it&departureCity={id_departure}&arrivalCity={id_arrival}&rideDate={departureDate}&adult=1")
    price_extracted = []
    duration_extracted = []
    try:
        elem = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME,'Price__priceWrapper___eDs_Y'))
        )
    except:
        if log:
            print("No results in date: " + departureDate)
        # if there are no results, we need to add a placeholder value
        price_extracted.append(None)
        duration_extracted.append(None)
    finally:
        prices = driver.find_elements(By.CLASS_NAME,'RoundBookButton__iconOnlyCTAPrice___FRjpw')
        durations = driver.find_elements(By.CLASS_NAME,'LocationsHorizontal__duration___rJ6rs')
        departureTime = driver.find_elements(By.CLASS_NAME,'LocationsHorizontal__time___SaJCp')
        for price in prices:
            #convert contaent of price to string
            price_text = str(price.get_attribute("outerHTML")).strip().replace('€', '')
            price_units = price_text.split("search-result-prices\">")[1].split("<sup>")[0].replace(',', '.')
            price_cents = price_text.split("<sup>,")[1].split("</sup>")[0]
            price_extracted.append(float(price_units + '.' + price_cents))
            duration_text = str(durations[prices.index(price)].get_attribute("outerHTML")).strip()
            duration_text = duration_text.split("search-result-duration\">")[1].split(" h</span>")[0]
            # convert duration from format hh:mm to hours
            duration_extracted.append(round((int(duration_text.split(":")[0]) * 60 + int(duration_text.split(":")[1]))/60,2))
        if log:
            print(f"Prices: {price_extracted}, Durations: {duration_extracted}")
        return price_extracted, duration_extracted

def get_min_max_price_duration(departureCity, arrivalCity, date, driver, log=False):

    # get the price and duration
    price, duration = get_price_duration(departureCity, arrivalCity, date, driver, log=log)

    # take the min and max price
    min_price = min(price)
    max_price = max(price)
    # take the duration of min and max price
    min_duration = duration[price.index(min_price)]
    max_duration = duration[price.index(max_price)]
        
    if log:
        print(f"min_price: {min_price}, max_price: {max_price}, min_duration: {min_duration}, max_duration: {max_duration}")
    return min_price, max_price, min_duration, max_duration

def plot_prices_duration(dates, lowest_prices, highest_prices, duration_lowest_prices, duration_highest_prices, departureCity, arrivalCity):
    
    # convert dates to datetime objects
    dates = [datetime.strptime(date, "%d.%m.%Y").date() for date in dates]
    
    # create the plot
    fig, (ax1,ax2) = plt.subplots(2,1)
    # set font size
    plt.rcParams.update({'font.size': 8})
    # plot max and min prices
    ax1.plot(dates, lowest_prices, label="lowest price")
    ax1.plot(dates, highest_prices, label="highest price")
    ax1.set_title(f"Lowest and highest prices from {departureCity} to {arrivalCity}")
    # hide x labels
    ax1.xaxis.set_visible(False)
    ax1.set_xlabel(f"Dates of {dates[0].month}")
    ax1.set_ylabel("Price (€)")
    ax1.legend()
    # plot max and min durations
    ax2.plot(dates, duration_lowest_prices, label="lowest duration")
    ax2.plot(dates, duration_highest_prices, label="highest duration")
    ax2.set_title(f"Lowest and highest durations from {departureCity} to {arrivalCity}")

    ax2.set_xlabel(f"Dates of {dates[0].month}")
    ax2.set_ylabel("Duration (h)")
    ax2.legend()

    # rotate x labels
    plt.xticks(rotation=90)
    # show the plot
    plt.show()



# flixbus endpoints

# https://global.api.flixbus.com/search/autocomplete/cities?q=Venezia&lang=it&country=it&flixbus_cities_only=false
# https://global.api.flixbus.com/cms/cities?language=it&country=IT
# https://d1ioiftasz4l3w.cloudfront.net/cities/_search
# https://d1ioiftasz4l3w.cloudfront.net/cities_v2/_search
# https://global.api.flixbus.com/cms/cities/40de90ff-8646-11e6-9066-549f350fcb0c/reachable?language=it&country=IT
# https://global.api.flixbus.com/search/service/cities/details?locale=it&from_city_id=1194


# solo andata
#https://shop.flixbus.it/search?_locale=it&departureCity=3738&arrivalCity=94&rideDate=19.02.2023&adult=1