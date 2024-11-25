from json import load
import os
import logging as logger
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# temporary local user config
homedir          = os.path.expanduser('~')
alpaca_user_conf = open(os.path.join(homedir,'.config/alpaca/paper_user.json'),'r')
alpaca_user      = load(alpaca_user_conf)

# No keys required for crypto data
client = StockHistoricalDataClient(alpaca_user.get("key"), alpaca_user.get("secret"))

# Creating request object
request_params = StockBarsRequest(
  symbol_or_symbols=["SPY"],
  timeframe=TimeFrame.Day,
  start="2022-09-01",
  end="2022-09-07"
)

# Retrieve daily bars for Bitcoin in a DataFrame and printing it
spy_bars = client.get_stock_bars(request_params)

# Convert to dataframe
print(spy_bars.df)