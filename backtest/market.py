import pandas as pd
from datetime import timedelta

class Transaction:
    def __init__(self, record: pd.Series):
        self.sender = record.sender
        self.amount0 = record.amount0
        self.amount1 = record.amount1
        self.amountUSD = record.amountUSD
        self.timestamp = record.timestamp
        self.price = record.price
        

class MarketInfo:
    # methodology:
    # load the dataframe in the market class
    # calibrate the parameters used to simulate the trader behavior
    # simulate some new orders usinng the function generate_tx and will return a row of a dataframme 
    # simulated sequenctial transactions
    # Take a rolling windows of the past 1 million tx for instance
    # Perform all the signle trades analysis, in term of pnl anf LVR percent
    # Aggregate the metrics to get the trader perfs 
    # Charge the fee per trader

    def __init__(self,
                 market_prices: pd.Series,
                 amm_delay: timedelta,
                 fee_rate: float,
                 pool_infos: dict,
                 len_simulation: int,
                 ):
        self.market_prices = market_prices
        self.amm_delay = amm_delay

    def _search(self, query_time):
        idx = self.market_prices.index.searchsorted(query_time)
        # Get the closest entry prior to the query datetime
        return self.market_prices.iloc[max(idx-1, 0)]

    def get_price_for_trader(self, query_time):
        return self._search(query_time)
    
    def load_data(self, data_path):
        self.data = pd.read_csv(data_path)
        
    def prepare_data(self):
        # compute the metrics we need to simulate fake trader
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], unit='s')
        self.data.set_index('timestamp', inplace=True)
        self.data.sort_index(inplace=True)
        
    def calibrate_traders():
        # calibrate the different poisson process for the trader behavior
        pass

    def generate_tx(self, trader, query_time):
        # simulate a new order for the trader
        pass
    
    
        
    def get_delayed_price_for_amm(self, query_time):
        delayed_time = query_time - self.amm_delay
        return self._search(delayed_time)