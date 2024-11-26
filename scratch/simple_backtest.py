from json import load
import os
import logging as logger
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from datetime import datetime

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


def get_historical_performance_for_ticker(ticker, timeframe = TimeFrame.Day, start = "2023-01-01", end = "2023-12-31", plot=True):
    """
    Gets a performance dataframe for a ticker by given timeframe intervals on [start,end].
    Also generates a line plot by default for this data

    params:
        ticker (str): ticker for get performance data
        timeframe (TimeFrame): interval for each point
        start (str): YYYY-MM-DD string when data starts
        end (str): YYYY-MM-DD string when data end
    
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
        end (str): YYYY-MM-DD string when data end
    
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
    strategy = pd.concat([crossover[[ticker, 'order']], crossunder[[ticker,'order']]]).sort_index()

    return strategy

def get_backtest(ticker, historical_data, strategy, equity, plot = True):
    """
    Gets portfolio for any given ticker, performance of ticker, strategy and portfolio equity

    params:
        ticker (str): ticker we are backtesting on
        historical_data (df): historical performance data we are backtesting over
        strategy (df): strategy data which informs when to buy/sell
        equity (num): total $ we are using for strategy
    
    returns:
        pandas dataframe: portfolio under strategy and also just buying & holding the ticker
    """
    # new dataframe with market data and strategy merged
    portfolio = pd.merge(historical_data, strategy, how='outer', left_index=True, right_index=True)

    # "backtest" of our buy and hold strategies
    portfolio[f'{ticker}_buy_&_hold'] = (portfolio[f'{ticker}_return'] + 1) * equity

    # forward fill any missing data points in our buy & hold strategies 
    # and forward fill BTC_daily_return for missing data points
    portfolio[[f'{ticker}_buy_&_hold']] = portfolio[[f'{ticker}_buy_&_hold']].ffill()

    ### Begin backtest
    active_position = False

    # Iterate row by row of our historical data
    for index, row in portfolio.iterrows():
        
        # change state of position
        if row['order'] == 'buy':
            active_position = True
        elif row['order'] == 'sell':
            active_position = False
        
        # update strategy equity
        if active_position:
            portfolio.loc[index, f'strategy'] = (row[f'{ticker}_daily_return'] + 1) * equity
            equity = portfolio.loc[index, f'strategy']
        else:
            portfolio.loc[index, f'strategy'] = equity

    if plot:
        fig = px.line(portfolio[['strategy', f'{ticker}_buy_&_hold']])
        fig.show()

    return portfolio

def calc_sharpe_ratio(ticker, backtest_portfolio, start_date, end_date):
    """
    Calculates the annualized Sharpe ratio for a given backtest portfolio

    params:
        ticker (str): ticker we backtested on
        backtest_portfolio (df): backtesting data
        start_date (str): YYYY-MM-DD string when data starts
        end_date (str): YYYY-MM-DD string when data end
    
    returns:
        numeric: annualized Sharpe ratio
    """

    backtest_portfolio['stategy_daily_returns'] = backtest_portfolio['strategy'].pct_change()

    # calculate averages and STD
    mean_daily_return = backtest_portfolio['stategy_daily_returns'].mean()
    std_daily_return  = backtest_portfolio['stategy_daily_returns'].std()
    ticker_mean_daily_return = backtest_portfolio[f'{ticker}_daily_return'].mean()

    # calculate number of trading days
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end   = datetime.strptime(end_date  , "%Y-%m-%d").date()
    trading_days = (end - start).days

    daily_sharpe_ratio = (mean_daily_return - ticker_mean_daily_return) / std_daily_return

    # annualized sharpe ratio
    return daily_sharpe_ratio * (trading_days ** 0.5)

# Backtest parameters
tickers = ["SPY"]
timeframe = TimeFrame.Day
start = "2023-01-01"
end = "2023-12-31"

spy_performance = get_historical_performance_for_ticker('SPY', timeframe, start, end, False)

spy_sma_crossover_strategy = get_sma_crossover_strategy('SPY', timeframe, start, end, False)

spy_sma_crossover_backtest = get_backtest('SPY', spy_performance, spy_sma_crossover_strategy, 10000)

print(spy_sma_crossover_backtest)

sharpe_ratio = calc_sharpe_ratio('SPY',spy_sma_crossover_backtest, start, end)

print(f"Annualized sharpe ratio:{sharpe_ratio}")