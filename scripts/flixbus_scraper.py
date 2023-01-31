from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.utils_functions import *

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)

departureCity = "Padova"
arrivalCity = "Trento"

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

# plot in a grid 1x2 prices and durations
plot_prices_duration(dates, lowest_prices, highest_prices, 
    duration_lowest_prices, duration_highest_prices, departureCity, arrivalCity)

driver.quit()
