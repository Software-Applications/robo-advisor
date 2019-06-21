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


def get_response(symbol):
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(request_url)
    #breakpoint()
    parsed_response = json.loads(response.text)
    return parsed_response

def to_usd(dollar_amt):
    return "${0:,.2f}".format(dollar_amt)


def to_date(date_value):
    date_p = datetime.datetime.strptime(date_value, '%Y-%m-%d')
    return date_p

def user_input():
    user_input = input("ENTER DESIRED STOCK SYMBOLS, SEPERATED BY COMMAS:")
    return user_input


# STEP 1: INFORMATION INPUT

stock_symbols = user_input()

# this splits user input and creates a list of stock symbols. Required for looping
symbols = re.findall(r'[^,;.\s]+', stock_symbols)

# STEP 2: VAIDATION AND GET REQUEST

# user input validation to check whether user input has 4 characters and is not numberic

stock_data = []
for s in symbols:
    if len(s) != 4 or s.isnumeric == True:
        print("You seem to have entered an invalid entry. Please enter correct stock identifiers.")
        break
    else:
    
        stock_data.append(get_response(s))
    
#breakpoint()
# At this point i have a list of nested dictionaries.

# STEP 3: PARSE THE DATA TO GET

#meta = [meta["Meta Data"] for meta in stock_data ]
#breakpoint()

now = datetime.datetime.now()
now_formatted = now.strftime("%Y-%m-%d %H:%M:%S")

# necessary to determined 52 weeks high and low
offset_weeks = datetime.timedelta(weeks = 52)


for item in stock_data:
    symbol = item['Meta Data']['2. Symbol']
    last_refreshed = item['Meta Data']['3. Last Refreshed']   
    date_keys = list(item["Time Series (Daily)"].keys())
    
    date_keys_f = [to_date(d) for d in date_keys]

    latest_day = max(date_keys_f)
    latest_day_ly = latest_day - offset_weeks
    date_keys_52weeks_f = [to_date(d).strftime("%Y-%m-%d") for d in date_keys if to_date(d) <= latest_day and to_date(d) >=latest_day_ly]
    #breakpoint()
    latest_day_f = latest_day.strftime("%Y-%m-%d")
    #breakpoint() 

    latest_stock_info = item["Time Series (Daily)"][latest_day_f]
    #breakpoint()

    latest_close = float(latest_stock_info['4. close'])
    latest_close_f = to_usd(float(latest_stock_info['4. close']))
    #breakpoint()

    high_price = []
    low_price = []
    for date in date_keys_52weeks_f:
        timeseries_meta = item["Time Series (Daily)"][date]
        daily_high = timeseries_meta["2. high"]
        daily_low = timeseries_meta["3. low"]
        high_price.append(daily_high)
        high_price_f = [float(i) for i in high_price]
        low_price.append(daily_low)
        low_price_f = [float(i) for i in low_price]
    
    recent_high = max(high_price_f)
    recent_high_f = to_usd(max(high_price_f))   
    recent_low = min(low_price_f)    
    recent_low_f = to_usd(min(low_price_f))   
    high_price.clear()
    low_price.clear()
    sensitivity_factor_low = latest_close / min(low_price_f)
    #sensitivity_factor_high = latest_close / recent_high

    if sensitivity_factor_low > 0 and sensitivity_factor_low <= 1.05:
        recommendation = "BUY!!"
        recommendation_reason = "THE CURRENT CLOSING PRICE IS AROUND THE LAST 52 WEEKS LOWEST PRICE. YOU MUST BUY IT"
    elif sensitivity_factor_low > 1.05 and sensitivity_factor_low <= 1.25:
        recommendation = "WE NEED TO DO A THROUGH EVALUATION OF THIS STOCK. BOOK AN APOINTMENT WITH US NOW"
        recommendation_reason = "THE CURRENT CLOSING IS INBETWEEN 52 WEEKS HIGH AND 52 WEEKS LOW. WE NEED TO CONSIDER ADDITIONAL FACTORS BEFORE YOU CAM BUY THIS STOCK"
    else:
        recommendation = "DO NOT BUY"
        recommendation_reason = "OUR DATA SUGGESTS THAT THE PRICE COULD GO FURTHER LOW OR THE STOCK HAS PICKED UP SUFFICIENTLY FROM RECENT LOW THAT IF IT GOES DOWN NOW, YOU COULD INCUR A HUGE LOSS"


    print("-------------------------")
    print(f"SELECTED SYMBOL: {symbol}")
    print("-------------------------")
    print("REQUESTING STOCK MARKET DATA...")
    print(f"REQUEST AT: {now_formatted}")      
    print("-------------------------")
    print(f"LATEST DAY: {last_refreshed}")
    print(f"LATEST CLOSE: {latest_close_f}")
    print(f"52 WEEKS HIGH: {recent_high_f}")
    print(f"52 WEEKS LOW: {recent_low_f}")
    print("-------------------------")
    print(f"RECOMMENDATION: {recommendation}")
    print(f"RECOMMENDATION REASON: {recommendation_reason}")
    print("-------------------------")
    print("HAPPY INVESTING!")
    print("-------------------------")
    print("\n")
    