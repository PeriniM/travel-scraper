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

# flixbus endpoints

# https://global.api.flixbus.com/search/autocomplete/cities?q=Venezia&lang=it&country=it&flixbus_cities_only=false
# https://global.api.flixbus.com/cms/cities?language=it&country=IT
# https://d1ioiftasz4l3w.cloudfront.net/cities/_search
# https://d1ioiftasz4l3w.cloudfront.net/cities_v2/_search
# https://global.api.flixbus.com/cms/cities/40de90ff-8646-11e6-9066-549f350fcb0c/reachable?language=it&country=IT
# https://global.api.flixbus.com/search/service/cities/details?locale=it&from_city_id=1194


# solo andata
#https://shop.flixbus.it/search?_locale=it&departureCity=3738&arrivalCity=94&rideDate=19.02.2023&adult=1

def get_city_legacy_id(city_name):
    response = requests.get(f"https://global.api.flixbus.com/search/autocomplete/cities?q={city_name}")
    data = json.loads(response.text)
    best_match = max(data, key=lambda x: x["score"])
    return best_match["legacy_id"]

def get_dates(month, year, separator="."):
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

dates = get_dates(2, 2023)
print(dates)
departureCity = "Trento"
arrivalCity = "Amburgo"
id_departure = get_city_legacy_id(departureCity)
id_arrival = get_city_legacy_id(arrivalCity)
print(id_departure, id_arrival)
lowest_prices_going = []
highest_prices_going = []
lowest_prices_return = []
highest_prices_return = []
# get prices for each date of the month going
for date in dates:
    departureDate = date
    driver.get(f"https://shop.flixbus.it/search?_locale=it&departureCity={id_departure}&arrivalCity={id_arrival}&rideDate={departureDate}&adult=1")
    price_unique = []
    try:
        elem = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME,'Price__priceWrapper___eDs_Y'))
        )
    except:
        print("no results")
        # if there are no results, we need to add a placeholder value
        lowest_prices_going.append(None)
        highest_prices_going.append(None)
        continue
    finally:
        prices = driver.find_elements(By.CLASS_NAME,'Price__priceWrapper___eDs_Y')
        for price in prices:
            #convert contaent of price to string
            price_text = str(price.get_attribute("outerHTML")).strip().replace('€', '')
            price_units = price_text.split("search-result-prices\">")[1].split("<sup>")[0].replace(',', '.')
            price_cents = price_text.split("<sup>,")[1].split("</sup>")[0]
            price_duplicated = float(price_units + '.' + price_cents)
            # prices are duplicated, so we need to remove them
            if price_duplicated not in price_unique:
                price_unique.append(price_duplicated)
    lowest_prices_going.append(min(price_unique))
    highest_prices_going.append(max(price_unique))
    print(price_unique)
        
# get prices for each date of the month returning
for date in dates:
    departureDate = date
    driver.get(f"https://shop.flixbus.it/search?_locale=it&departureCity={id_arrival}&arrivalCity={id_departure}&rideDate={departureDate}&adult=1")
    price_unique = []
    try:
        elem = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME,'Price__priceWrapper___eDs_Y'))
        )
    except:
        print("no results")
        # if there are no results, we need to add a placeholder value
        lowest_prices_return.append(None)
        highest_prices_return.append(None)
        continue
    finally:
        prices = driver.find_elements(By.CLASS_NAME,'Price__priceWrapper___eDs_Y')
        for price in prices:
            #convert contaent of price to string
            price_text = str(price.get_attribute("outerHTML")).strip().replace('€', '')
            price_units = price_text.split("search-result-prices\">")[1].split("<sup>")[0].replace(',', '.')
            price_cents = price_text.split("<sup>,")[1].split("</sup>")[0]
            price_duplicated = float(price_units + '.' + price_cents)
            # prices are duplicated, so we need to remove them
            if price_duplicated not in price_unique:
                price_unique.append(price_duplicated)
    lowest_prices_return.append(min(price_unique))
    highest_prices_return.append(max(price_unique))
    print(price_unique)

# plot the results in a graph
# convert dates to datetime objects
dates = [datetime.strptime(date, "%d.%m.%Y").date() for date in dates]
# convert None values to NaN
lowest_prices_going = [None if price is None else price for price in lowest_prices_going]
highest_prices_going = [None if price is None else price for price in highest_prices_going]
lowest_prices_return = [None if price is None else price for price in lowest_prices_return]
highest_prices_return = [None if price is None else price for price in highest_prices_return]

# plot in a grid 2x1 going and returning
fig, (ax1, ax2) = plt.subplots(2,1)
# set font size
plt.rcParams.update({'font.size': 8})
# plot going
ax1.plot(dates, lowest_prices_going, label="lowest price")
ax1.plot(dates, highest_prices_going, label="highest price")
ax1.set_title(f"Lowest and highest prices from {departureCity} to {arrivalCity}")
# hide x labels
ax1.xaxis.set_visible(False)
ax1.set_xlabel("Dates of {dates[0].month}")
ax1.set_ylabel("Price (€)")
ax1.legend()
# plot returning
ax2.plot(dates, lowest_prices_return, label="lowest price")
ax2.plot(dates, highest_prices_return, label="highest price")
ax2.set_title(f"Lowest and highest prices from {arrivalCity} to {departureCity}")
# rotate x labels
plt.xticks(rotation=90)
ax2.set_xlabel("Dates of {dates[0].month}")
ax2.set_ylabel("Price (€)")
ax2.legend()
# show the plot
plt.show()

driver.quit()
