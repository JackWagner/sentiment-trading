from strategies.sma_crossover import SMA_crossover
from scrapers.discord.channel import Channel

# Defining main function
def main():
    #crossover_strategy = SMA_crossover("SPY")    
    #print(f'SMA_crossover("SPY") object: {crossover_strategy}')
    #crossover_strategy.get_backtest(start="2022-01-01", end="2023-12-31")    
    snp_channel = Channel('1069894924465610752')
    retrieve_messages = snp_channel.get_messages()

# Using the special variable 
# __name__
if __name__=="__main__":
    main()