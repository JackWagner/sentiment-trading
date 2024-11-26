from strategy import Strategy

# Defining main function
def main():
    print("Hello")
    spy_simple_strat = Strategy("simple strategy", "SPY")
    print(spy_simple_strat)


# Using the special variable 
# __name__
if __name__=="__main__":
    main()