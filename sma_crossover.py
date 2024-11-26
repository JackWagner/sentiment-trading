# Base class
from strategy import Strategy

# Alpaca
from alpaca.data.timeframe import TimeFrame

# Plotly for charting
import plotly.graph_objects as go
import plotly.express as px

class SMA_crossover(Strategy):
    '''
    The SMA_crossover object determines when to buy/sell from long term and short term trend crossing over/under each other.

    Args:
        ticker(str): The ticker the strategy determines when to buy/sell on

    Attributes:
        name (str): Name of the strategy
        ticker(str): The ticker the strategy determines when to buy/sell on
    '''
    def __init__(self, ticker) -> None:
        self.name = 'Simple Moving Average Crossover'
        self.ticker = ticker

    def get_strategy(ticker, timeframe = TimeFrame.Day, start = "2023-01-01", end = "2023-12-31", slow_period = 13, fast_period = 5, plot=True):
        '''
        Gets strategy dataframe using the SMA crossover rules for a ticker by given timeframe intervals on [start,end].

        params:
            ticker (str): ticker for get performance data
            timeframe (TimeFrame): interval for each point
            start (str): YYYY-MM-DD string when data starts
            end (str): YYYY-MM-DD string when data end
        
        returns:
            pandas dataframe: crossover strategy dataframe
        '''
        data = get_historical_performance_for_ticker(ticker, timeframe, start, end, False)

        # Computing the 5-day SMA and 13-day SMA
        data['slow_SMA'] = data[ticker].rolling(slow_period).mean()
        data['fast_SMA'] = data[ticker].rolling(fast_period).mean()

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
        strategy = pd.concat([crossover[[ticker, 'order']], crossunder[[ticker,'order']]]).sort_index()

        if plot:
            # Plot green upward facing triangles at crossovers
            fig1 = px.scatter(crossover, x=crossover.index, y='slow_SMA', \
                            color_discrete_sequence=['green'], symbol_sequence=[49])

            # Plot red downward facing triangles at crossunders
            fig2 = px.scatter(crossunder, x=crossunder.index, y='fast_SMA', \
                            color_discrete_sequence=['red'], symbol_sequence=[50])

            # Plot slow sma, fast sma and price
            fig3 = data.plot(y=[ticker, 'fast_SMA', 'slow_SMA'])

            fig4 = go.Figure(data=fig1.data + fig2.data + fig3.data)
            fig4.update_traces(marker={'size': 13})
            fig4.show()

        return strategy