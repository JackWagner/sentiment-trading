from logging import logger

class Security:
    '''
    The Security object represents a tradable financial asset

    Args:
        ticker(str): The ticker for the asset

    Attributes:
        ticker(str): The ticker the strategy determines when to buy/sell on
        name (str): Name of the asset
    '''
    def __init__(self, ticker) -> None:
        self.ticker = ticker

        self.name = None


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