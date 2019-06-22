# app/robo_advisor.py

import requests
from dotenv import load_dotenv
import datetime
import os
import csv
import re
import json
from pprint import pprint

# Alphavantage API Information
load_dotenv() #> loads contents of the .env file into the script's environment
API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "Authentication Error!!") # default to using the "demo" key if an Env Var is not supplied

# Functions
def get_response(symbol):
    #request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(request_url)
    parsed_response = json.loads(response.text)
    return parsed_response

def to_usd(dollar_amt):
    return "${0:,.2f}".format(dollar_amt)

def to_fnum(numb):
    return '{0:,}'.format(numb)


def to_date(date_value):
    date_p = datetime.datetime.strptime(date_value, '%Y-%m-%d')
    return date_p

def user_input():
    user_input = input("ENTER DESIRED STOCK SYMBOLS. EACH STOCK SHOULD HAVE 4 CHARACTERS AND BE SEPERATED BY COMMAS:")
    return user_input

if __name__ == "__main__":

    ##### STEP 1: INFORMATION INPUT

    stock_symbols = user_input()

    # this splits user input and creates a list of stock symbols. Required for looping
    symbol_parser = re.findall(r'[^",;.\s]+', stock_symbols)
    symbols = [s.lower() for s in symbol_parser]

    ##### STEP 2: VAIDATION AND GET REQUEST

    stock_data = []
    error = "Error Message"

    for s in symbols:
        # initial validtion to check if the input has required number of characters and is not a number
        if len(s) != 4 or s.isnumeric == True:
            print(f"OOPS! {s} is not a valid entry. Please enter correct stock identifiers.")
            break
        else:
            response = get_response(s)

            # checks if the stock really exists
            if not error in response.keys():
                stock_data.append(response)
            else:
                print("\n")
                print(f"OOPS! STOCK DATA FOR {s} IS NOT AVAILABLE. DID YOU MAKE A CORRECT ENTRY?")
                print("\n")
                continue

    # At this point i have a list of nested dictionaries of response data

    ##### STEP 3: PARSE THE LIST TO DERIVE OUTPUT

    now = datetime.datetime.now()
    now_formatted = now.strftime("%Y-%m-%d %H:%M:%S")

    # necessary to determine 52 weeks high and low
    offset_days = datetime.timedelta(days = 365)


    for item in stock_data:

        # Meta data; latest stock info; other necessary variables to get going
        symbol = item['Meta Data']['2. Symbol']
        last_refreshed = item['Meta Data']['3. Last Refreshed']   
        #date_keys = list(item["Time Series (Daily)"].keys())
        date_keys = list(item["Weekly Time Series"].keys())
        date_keys_f = [to_date(d) for d in date_keys]
        latest_day = max(date_keys_f)
        latest_day_52weeks = latest_day - offset_days
        date_keys_52weeks_f = [to_date(d).strftime("%Y-%m-%d") for d in date_keys if to_date(d) <= latest_day and to_date(d) >=latest_day_52weeks]
        latest_day_f = latest_day.strftime("%Y-%m-%d")
        #latest_stock_info = item["Time Series (Daily)"][latest_day_f]
        latest_stock_info = item["Weekly Time Series"][latest_day_f]


        latest_close = float(latest_stock_info['4. close'])
        latest_close_f = to_usd(float(latest_stock_info['4. close']))

        high_price = []
        low_price = []
        file_name = os.path.join(os.getcwd(), "data", f"prices_{symbol}.csv")

        # removes the csv file if it exists
        if os.path.exists(file_name):
            os.remove(file_name)

        # writes csv header
        with open(file_name, "w") as csv_header:
            header = csv.DictWriter(csv_header, fieldnames = ["timestamp", "open", "high", "low", "close", "volume"])
            header.writeheader()

        # looping through last 52 weeks to extract required variables. useful for writing csv and creating lists for high prices and low prices
        # currently the prgram is looking at less than 52 weeks data because the data set has less than 52 weeks
        for date in date_keys_52weeks_f:
            #timeseries_meta = item["Time Series (Daily)"][date]
            timeseries_meta = item["Weekly Time Series"][date]
            weekly_open = timeseries_meta["1. open"]
            weekly_high = timeseries_meta["2. high"]
            weekly_low = timeseries_meta["3. low"]
            weekly_close = timeseries_meta["4. close"]
            weekly_volume = timeseries_meta["5. volume"]
            high_price.append(weekly_high)
            high_price_f = [float(i) for i in high_price]
            low_price.append(weekly_low)
            low_price_f = [float(i) for i in low_price]
            
            # writes values in csv file
            with open(file_name, "a") as csv_detail:            
                writer = csv.DictWriter(csv_detail, fieldnames = ["timestamp", "open", "high", "low", "close", "volume"])
                writer.writerow({"timestamp": date, "open": weekly_open, "high": weekly_high, "low": weekly_low, "close": weekly_close,"volume": weekly_volume})


        # variables needed to calulate recommendation engine; high price and low price
        recent_high = max(high_price_f)
        recent_high_f = to_usd(max(high_price_f))   
        recent_low = min(low_price_f)    
        recent_low_f = to_usd(min(low_price_f))   
        high_price.clear()
        low_price.clear()
        sensitivity_factor_low = latest_close / min(low_price_f)

        # recommendation engine
        if sensitivity_factor_low > 0 and sensitivity_factor_low <= 1.05:
            recommendation = "BUY!!"
            recommendation_reason = "THE CURRENT CLOSING PRICE IS AROUND LOWEST IN LAST 52 WEEKS. YOU MUST BUY IT"
        elif sensitivity_factor_low > 1.05 and sensitivity_factor_low <= 1.25:
            recommendation = "WE NEED TO DO A THROUGH EVALUATION OF THIS STOCK. BOOK AN APOINTMENT WITH US NOW"
            recommendation_reason = "THE CURRENT CLOSING IS INBETWEEN LAST 52 WEEKS HIGH AND LOW. WE NEED TO CONSIDER ADDITIONAL FACTORS BEFORE YOU CAN BUY THIS STOCK"
        else:
            recommendation = "DO NOT BUY"
            recommendation_reason = "OUR DATA SUGGESTS THAT THE PRICE COULD GO FURTHER LOW OR THE STOCK HAS PICKED UP SUFFICIENTLY FROM RECENT 52 WEEKS LOW THAT IF IT GOES DOWN NOW, YOU COULD INCUR A HUGE LOSS"

        # writing recommendation to CLI
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
        