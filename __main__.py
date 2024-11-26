from strategies.sma_crossover import SMA_crossover

# Defining main function
def main():
    crossover_strategy = SMA_crossover("spy")
    print(f'SMA_crossover("spy") object: {crossover_strategy}')
    crossover_strategy.get_strategy(start="2022-01-01", end="2023-12-31")    


# Using the special variable 
# __name__
if __name__=="__main__":
    main()