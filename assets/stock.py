# load environment variables
from os import path
from json import load

# Stock is a child of Security
from assets.security import Security

# Retrieving stock history
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Plotly for charting
import plotly.express as px

# temporary local user config
homedir          = path.expanduser('~')
alpaca_user_conf = open(path.join(homedir,'.config/alpaca/paper_user.json'),'r')
alpaca_user      = load(alpaca_user_conf)

# No keys required for crypto data
client = StockHistoricalDataClient(alpaca_user.get("key"), alpaca_user.get("secret"))

class Stock(Security):
    '''
    The Stock object is a tradable financial asset that exists a public stock exchange

    Args:
         ticker(str): The ticker for the stock
        ,mid(str): Market Identifier Code, default is XNYS (NYSE)

    Attributes:
         ticker(str): The ticker the strategy determines when to buy/sell on
        ,mid(str): Market Identifier Code identified where the given stock is traded, typically XNYS (NYSE) or XNAS (Nasdaq)
    '''
    def __init__(self, ticker: str, mid: str = 'XNYS') -> None:
        self.mid = mid

    def __str__(self):
        return f"Stock with ticker {self.ticker} in market {self.mid}"

    def get_historical_data(self, start_date, end_date, timeframe = TimeFrame.Day):
        """
        Returns historical data for stock by given timeframe intervals on [start,end].

        params:
            start (str): YYYY-MM-DD string when data starts
            end (str): YYYY-MM-DD string when data end
            timeframe (TimeFrame): interval for each point, default is a day
        
        returns:
            pandas dataframe: historical stock value dataframe
        """
        result = None
        try:
            request_params = StockBarsRequest(
            symbol_or_symbols=[self.ticker],
            timeframe=timeframe,
            start=start_date,
            end=end_date
            )
            result = client.get_stock_bars(request_params).df
        except Exception as e:
            print(e)

        return result

    def get_performance_data(self, historical_data):
        """
        Returns a stocks performance over some historical dataframe.

        params:
            historical_date (df): dataframe produced by get_historical_data()
        
        returns:
            pandas dataframe: historical performance dataframe
        """

        # Filter down to closing price
        data = data.filter(['close'])

        # remove multi-index, set to date
        data.reset_index(inplace=True)
        data.set_index('timestamp', inplace=True)
        data.index.name = 'date'
        data = data.ffill()

        # calculate daily and cumulative returns on stock
        data[f'daily_return'] = data['close'].pct_change()
        data[f'total_return']       = data[f'daily_return'].add(1).cumprod().sub(1)

        return data

    def plot_historical_data(self, historical_data) -> None:
        '''Generates a plot of daily closing value from historical data'''
        fig = px.line(historical_data, x = historical_data.index, y = ['close'])
        fig.show()

    def plot_performance_data(self, performance_data) -> None:
        '''Generates a plot of daily and total return from performance data'''
        fig = px.line(performance_data, x = performance_data.index, y = ['daily_return','total_return'])
        fig.show()