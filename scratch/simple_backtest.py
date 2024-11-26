from json import load
import os
import logging as logger
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# dataframe handling
import pandas as pd

# Plotly for charting
import plotly.graph_objects as go
import plotly.express as px

# Set default charting for pandas to plotly
pd.options.plotting.backend = "plotly"

# temporary local user config
homedir          = os.path.expanduser('~')
alpaca_user_conf = open(os.path.join(homedir,'.config/alpaca/paper_user.json'),'r')
alpaca_user      = load(alpaca_user_conf)

# No keys required for crypto data
client = StockHistoricalDataClient(alpaca_user.get("key"), alpaca_user.get("secret"))

# Backtest parameters
tickers = ["SPY"]
timeframe = TimeFrame.Day
start = "2023-01-01"
end = "2023-12-31"

def get_historical_performance_for_ticker(ticker, timeframe = TimeFrame.Day, start = "2023-01-01", end = "2023-12-31", plot=True):
    """
    This returns a performance dataframe for a ticker by given timeframe intervals between start and end dates.
    Also generates a line plot by default for this data

    params:
        ticker (str): ticker for get performance data
        timeframe (TimeFrame): interval for each point
        start (str): YYYY-MM-DD string when data starts
        end (str): YYYY-MM-DD string when data starts
    
    returns:
        pandas dataframe: timeframe series is index and values are percent change and daily returns
    """
    # Creating request object
    try:
        request_params = StockBarsRequest(
        symbol_or_symbols=[ticker],
        timeframe=timeframe,
        start=start,
        end=end
        )
    except Exception as e:
        print(e)

    # Retrieve daily bars for Bitcoin in a DataFrame and printing it
    data = client.get_stock_bars(request_params).df

    # Filter down to closing price
    data = data.filter(['close'])
    data.rename(columns={'close':ticker}, inplace=True)

    # remove multi-index, set to date
    data.reset_index(inplace=True)
    data.set_index('timestamp', inplace=True)
    data.index.name = 'date'
    data = data.ffill()

    # calculate data returns for BTC and SPY
    data['SPY_daily_return'] = data['SPY'].pct_change()
    data['SPY_return']       = data['SPY_daily_return'].add(1).cumprod().sub(1)

    if plot:
        fig = px.line(data,x=data.index, y=['SPY_return'])
        fig.show()

    return data

def backtest_sma(data):
    """
    This returns a performance dataframe for a ticker by given timeframe intervals between start and end dates.
    Also generates a line plot by default for this data

    params:
        data (df): performance data generated via get_historical_performance_for_ticker()
    
    returns:

    """


spy_performance = get_historical_performance_for_ticker('SPY', timeframe, start, end, True)