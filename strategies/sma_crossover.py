# Required classes
from strategies.strategy import Strategy
from assets.stock import Stock

# Alpaca
from alpaca.data.timeframe import TimeFrame

# Plotly for charting
import plotly.graph_objects as go
import plotly.express as px

# Pandas
import pandas as pd

class SMA_crossover(Strategy):
    '''
    The SMA_crossover object determines when to buy/sell from long term and short term trend crossing over/under each other.

    Args:
        ticker(str): The ticker the strategy determines when to buy/sell on

    Attributes:
        name (str): Name of the strategy
        stock (Stock): Stock object for the given ticker
    '''
    def __init__(self, ticker) -> None:
        self.name = 'Simple Moving Average Crossover'
        self.stock = Stock(ticker)
        super().__init__(self.name, ticker)

    def get_strategy(self, start = "2023-01-01", end = "2023-12-31", timeframe = TimeFrame.Day, slow_period = 13, fast_period = 5, plot = True):
        '''
        Gets strategy dataframe using the SMA crossover rules for a ticker by given timeframe intervals on [start,end].

        params:
            ticker (str): ticker for get performance data
            timeframe (TimeFrame): interval for each point
            start (str): YYYY-MM-DD string when data starts
            end (str): YYYY-MM-DD string when data end
            slow_period (int): number of days of long-term trend window
            fast_period (int): number of days of short-term trend window
            plot (bool): Whether or not to generate strategy figure
        
        returns:
            pandas dataframe: crossover strategy dataframe
        '''

        # Get performance data
        data = self.stock.get_performance_data(start, end, timeframe)

        # Computing the 5-day SMA and 13-day SMA
        data['slow_SMA'] = data['close'].rolling(slow_period).mean()
        data['fast_SMA'] = data['close'].rolling(fast_period).mean()

        data.dropna(inplace=True)

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
        strategy = pd.concat([crossover[['close', 'order']], crossunder[['close','order']]]).sort_index()

        if plot:

            # get both the closing value by interval and strategy
            plot_data = data.join(strategy['order'])

            print(plot_data)

            # Plot slow sma, fast sma and price
            fig = px.line(x = plot_data.index, y = plot_data['close'], title = str(self))
            
            # Plot green upward facing triangles at crossovers
            fig.add_trace(px.scatter(crossover, x=crossover.index, y='slow_SMA', color_discrete_sequence=['green'], symbol_sequence=[49]).data[0])

            # Plot red downward facing triangles at crossunders
            fig.add_trace(px.scatter(crossunder, x=crossunder.index, y='fast_SMA', color_discrete_sequence=['red'], symbol_sequence=[50]).data[0])

            fig.update_traces(marker={'size': 13})
            fig.show()

        return strategy

    def get_backtest(self, start = "2023-01-01", end = "2023-12-31", timeframe = TimeFrame.Day, slow_period = 13, fast_period = 5, equity = 10000, plot = True):
        """
        Gets portfolio using SME crossover strategy for a ticker by given timeframe intervals on [start,end].

        params:
            start (str): YYYY-MM-DD string when data starts
            end (str): YYYY-MM-DD string when data end
            timeframe (TimeFrame): interval for each point
            equity (num): total $ we are using for strategy
            plot (bool): Whether or not to generate backtest figure
        
        returns:
            pandas dataframe: portfolio under strategy and also just buying & holding the asset
        """

        performance_df = self.stock.get_performance_data(start, end, timeframe)
        strategy_df    = self.get_strategy(start, end, timeframe, slow_period, fast_period, plot)

        # new dataframe with market data and strategy merged
        portfolio = pd.merge(performance_df, strategy_df, how='outer', left_index=True, right_index=True)

        # "backtest" of our buy and hold strategies
        portfolio['buy_&_hold'] = (portfolio['total_return'] + 1) * equity

        # forward fill any missing data points in our buy & hold strategies 
        portfolio[['buy_&_hold']] = portfolio[['buy_&_hold']].ffill()

        ### Begin backtest
        active_position = False

        # Iterate row by row of our historical data
        for index, row in portfolio.iterrows():
            
            # change state of position
            if   row['order'] == 'buy':
                active_position = True
            elif row['order'] == 'sell':
                active_position = False
            
            # update strategy equity
            if active_position:
                portfolio.loc[index, 'strategy'] = (row['daily_return'] + 1) * equity
                equity = portfolio.loc[index, f'strategy']
            else:
                portfolio.loc[index, 'strategy'] = equity

        if plot:
            fig = px.line(portfolio[['strategy', 'buy_&_hold']], title = f"Backtest of {str(self)}")
            fig.show()

        return portfolio