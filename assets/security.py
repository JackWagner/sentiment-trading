class Security:
    '''
    The Security object represents a tradable financial asset

    Args:
        ticker(str): The ticker for the asset

    Attributes:
        ticker(str): The ticker the strategy determines when to buy/sell on
    '''
    def __init__(self, ticker: str) -> None:
        self.ticker = ticker

    def __str__(self):
        return f"Security with ticker {self.ticker}"
    
    def get_ticker(self):
        return self.ticker