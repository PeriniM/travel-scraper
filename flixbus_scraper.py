from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import matplotlib.pyplot as plt
from utils_functions import *

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

departureCity = "Trento"
arrivalCity = "Venezia"

dates = get_dates(2, 2023, separator=".", log=False)

lowest_prices = []
highest_prices = []
duration_lowest_prices = []
duration_highest_prices = []

# get prices for each date of the month going
for date in dates:
    result = get_min_max_price_duration(departureCity, arrivalCity, date, driver, log=True)

    lowest_prices.append(result[0])
    highest_prices.append(result[1])
    duration_lowest_prices.append(result[2])
    duration_highest_prices.append(result[3])

# convert dates to datetime objects
dates = [datetime.strptime(date, "%d.%m.%Y").date() for date in dates]
# convert durations to hours
duration_lowest_prices = [duration/60 for duration in duration_lowest_prices]
duration_highest_prices = [duration/60 for duration in duration_highest_prices]
# plot in a grid 1x2 prices and durations

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

driver.quit()
