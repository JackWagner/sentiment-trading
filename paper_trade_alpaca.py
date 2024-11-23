from json       import load
import os
import logging as logger
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

# temporary local user config
homedir      = os.path.expanduser('~')
alpaca_user_conf = open(os.path.join(homedir,'.ssh/alpaca_paper_user.json'),'r')
alpaca_user      = load(alpaca_user_conf)

# Pass API Key and Secret Key to TradingClient
trading_client = TradingClient(alpaca_user.get("key"), alpaca_user.get("secret"))

# Get our account information.
account = trading_client.get_account()

# Check if our account is restricted from trading.
if account.trading_blocked:
    print('Account is currently restricted from trading.')

# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))