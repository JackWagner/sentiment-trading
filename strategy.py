from logging import logger

class Strategy:
    '''
    The Strategy object determines when to buy/sell given real-time or historical data by some rule set

    Args:
        name (str): Name of the strategy
        ticker(str): The ticker the strategy determines when to buy/sell on

    Attributes:
        name (str): Name of the strategy
        ticker(str): The ticker the strategy determines when to buy/sell on
    '''
    def __init__(self, name, ticker) -> None:
        self.name = name
        self.ticker = ticker

    def __str__(self):
        return f"Strategy {self.name} on {self.ticker}"

    def set_ticker(self, ticker):
        '''Change the ticker without recreating a strategy object'''
        # :TO-DO create Asset class, which can generate historical/real-time performance data from Ticker
        self.ticker = ticker

    def get_name(self):
        return self.name
    
    def get_ticker(self):
        return self.ticker
    
    def get_backtest_df(self):
        print("No strategy defined in base class Strategy")
        pass