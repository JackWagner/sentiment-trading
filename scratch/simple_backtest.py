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
    Gets a performance dataframe for a ticker by given timeframe intervals on [start,end].
    Also generates a line plot by default for this data

    params:
        ticker (str): ticker for get performance data
        timeframe (TimeFrame): interval for each point
        start (str): YYYY-MM-DD string when data starts
        end (str): YYYY-MM-DD string when data starts
    
    returns:
        pandas dataframe: historical performance dataframe
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
    data[f'{ticker}_daily_return'] = data[ticker].pct_change()
    data[f'{ticker}_return']       = data[f'{ticker}_daily_return'].add(1).cumprod().sub(1)

    if plot:
        fig = px.line(data,x=data.index, y=[f'{ticker}_return'])
        fig.show()

    return data

def get_sma_crossover_strategy(ticker, timeframe = TimeFrame.Day, start = "2023-01-01", end = "2023-12-31", plot=True):
    """
    Gets strategy dataframe using the SMA crossover rules for a ticker by given timeframe intervals on [start,end].

    params:
        ticker (str): ticker for get performance data
        timeframe (TimeFrame): interval for each point
        start (str): YYYY-MM-DD string when data starts
        end (str): YYYY-MM-DD string when data starts
    
    returns:
        pandas dataframe: crossover strategy dataframe
    """

    data = get_historical_performance_for_ticker(ticker, timeframe, start, end, False)

    # periods for our SMA's
    slow_period = 13
    fast_period = 5

    # Computing the 5-day SMA and 13-day SMA
    data['slow_SMA'] = data[ticker].rolling(slow_period).mean()
    data['fast_SMA'] = data[ticker].rolling(fast_period).mean()

    data.dropna(inplace=True)

    if plot:
        fig = px.line(data,x=data.index, y=[ticker, 'slow_SMA', 'fast_SMA'])
        fig.show()

    # Strategy:
    # calculating when 5-day SMA crosses over 13-day SMA
    crossover = data[(data['fast_SMA'] > data['slow_SMA']) \
        & (data['fast_SMA'].shift() < data['slow_SMA'].shift())]
                        
    # calculating when 5-day SMA crosses unsw 13-day SMA
    crossunder = data[(data['fast_SMA'] < data['slow_SMA']) \
            & (data['fast_SMA'].shift() > data['slow_SMA'].shift())]

    # New column for orders
    crossover['order'] = 'buy'
    crossunder['order'] = 'sell'

    # Combine buys and sells into 1 data frame
    orders = pd.concat([crossover[[ticker, 'order']], crossunder[[ticker,'order']]]).sort_index()

    # new dataframe with market data and orders merged
    portfolio = pd.merge(data, orders, how='outer', left_index=True, right_index=True)

    return portfolio

spy_performance = get_historical_performance_for_ticker('SPY', timeframe, start, end, True)

spy_sma_crossover_strategy = get_sma_crossover_strategy('SPY', timeframe, start, end, True)

#print(spy_sma_crossover_strategy)

# "backtest" of our buy and hold strategies
# portfolio[f'{ticker}_buy_&_hold'] = (portfolio[f'{ticker}_return'] + 1) * 10000