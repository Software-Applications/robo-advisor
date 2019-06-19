# app/robo_advisor.py

# IMPORT ALL REQUIRED PACKAGES AND MODULES
import requests
import dotenv
import datetime
import os
import pprint
import csv
import re
#from data import *


# STEP 1: INFORMATION INPUT

stock_symbols = input("ENTER DESIRED STOCK SYMBOLS, SEPERATED BY COMMAS:")
print(stock_symbols)
#breakpoint()


# this splits user input and creates a list of stock symbols. Required for looping
stocks = re.findall(r'[^,;\s]+', stock_symbols)
print(stocks)
#breakpoint()

# user input validation to check whether user input has 4 characters and is not numberic
for s in stocks:
    if len(s) != 4 or s.isnumeric:
        print("You seem to have entered an invalid entry. Please enter correct stock identifiers.")
        break   # TODO: add a loop to ask user for input.
    else:
        pass    #TODO: i need to handle get requests here





print("-------------------------")
print("SELECTED SYMBOL: XYZ")
print("-------------------------")
print("REQUESTING STOCK MARKET DATA...")
print("REQUEST AT: 2018-02-20 02:00pm")
print("-------------------------")
print("LATEST DAY: 2018-02-20")
print("LATEST CLOSE: $100,000.00")
print("RECENT HIGH: $101,000.00")
print("RECENT LOW: $99,000.00")
print("-------------------------")
print("RECOMMENDATION: BUY!")
print("RECOMMENDATION REASON: TODO")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")