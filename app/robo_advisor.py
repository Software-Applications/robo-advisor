# app/robo_advisor.py

# IMPORT ALL REQUIRED PACKAGES AND MODULES
import requests
from dotenv import load_dotenv
import datetime
import os
from pprint import pprint
import csv
import re
import json
import pandas
#from data import *


load_dotenv() #> loads contents of the .env file into the script's environment

API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "Authentication Error!!") # default to using the "demo" key if an Env Var is not supplied

#breakpoint()

def get_response(symbol):
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(request_url)
    #breakpoint()
    parsed_response = json.loads(response.text)
    return parsed_response

#trial = get_response('MSFT')



# STEP 1: INFORMATION INPUT

stock_symbols = input("ENTER DESIRED STOCK SYMBOLS, SEPERATED BY COMMAS:")
#print(stock_symbols)
#breakpoint()


# this splits user input and creates a list of stock symbols. Required for looping
symbols = re.findall(r'[^,;.\s]+', stock_symbols)
#print(symbols)
#breakpoint()

# STEP 2: VAIDATION AND GET REQUEST

# user input validation to check whether user input has 4 characters and is not numberic

stock_data = []      # defining an empty list
for s in symbols:
    if len(s) != 4 or s.isnumeric == True:
        print("You seem to have entered an invalid entry. Please enter correct stock identifiers.")
        break   # TODO: add a loop to ask user for input.
    else:
        #request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={s}&apikey={API_KEY}"
        #breakpoint()
        #test_p = s
        stock_data.append(get_response(s))
        #breakpoint()

#breakpoint()
# At this point i have a list of nested dictionaries.

# STEP 3: PARSE THE DATA TO GET

meta = [meta["Meta Data"] for meta in stock_data ]
#timeseries = [ts["Time Series (Daily)"] for ts in stock_data]
#breakpoint()

price_list = []

for item in stock_data:
    symbol = item['Meta Data']['2. Symbol']
    last_refreshed = item['Meta Data']['3. Last Refreshed']   # TODO: Need to add AM/PM
    dates = list(item["Time Series (Daily)"].keys())
    latest_day = max(dates)       # TODO: Is this required? - I should probably convert the strings to date format and then do a max function
    #latest_close = [d for d["Time Series (Daily"] in item]
    #for day in item["Time Series (Daily)"]
    #pprint(item[1])
    latest_meta = [item["Time Series (Daily)"][latest_day]]
    #breakpoint()
    latest_close = latest_meta[0]['4. close']
    for date in dates:
        timeseries_meta = item["Time Series (Daily)"][date]
        daily_high = timeseries_meta["2. high"]
        price_list.append(daily_high)
        #breakpoint()
    recent_high = max(price_list)
    recent_low = min(price_list)
    breakpoint()

'''
for item in meta:
    print("-------------------------")
    print(f"SELECTED SYMBOL: {item['2. Symbol']}")
    print("-------------------------")
    print("REQUESTING STOCK MARKET DATA...")
    print(f"REQUEST AT: {item['3. Last Refreshed']}")
    print("-------------------------")


#breakpoint()







#print("LATEST DAY: 2018-02-20")
#print("LATEST CLOSE: $100,000.00")
#print("RECENT HIGH: $101,000.00")
#print("RECENT LOW: $99,000.00")
#print("-------------------------")
#print("RECOMMENDATION: BUY!")
#print("RECOMMENDATION REASON: TODO")
#print("-------------------------")
#print("HAPPY INVESTING!")
#print("-------------------------")

'''