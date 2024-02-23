from config import *

class ICEXMarketInfo:
    def __init__(self, market_prices: pd.Series, amm_delay: float):
        self.market_prices = market_prices
        self.amm_delay = timedelta(seconds=amm_delay)

    def _search(self, query_time):
        """Find the closet market price by a query timestamp"""
        idx = self.market_prices.index.searchsorted(query_time)
        # Get the closest entry prior to the query datetime
        return self.market_prices.iloc[max(idx-1, 0)]

    def get_price_for_trader(self, query_time):
        raise NotImplementedError

    def get_delayed_price_for_amm(self, query_time):
        raise NotImplementedError


class SimpleCEXMarketInfo(ICEXMarketInfo):
    def get_price_for_trader(self, query_time):
        return self._search(query_time)

    def get_delayed_price_for_amm(self, query_time):
        delayed_time = query_time - self.amm_delay
        return self._search(delayed_time)
    

class StochasticCEXMarketInfo(ICEXMarketInfo):
    """Supply market price info in a random process"""
    def __init__(self, market_prices: pd.Series, amm_delay: timedelta, time_sigma: float=10.0):
        super().__init__(market_prices, amm_delay)
        self.sigma = time_sigma
    
    def _search(self, query_time):
        """
        Find the closet market price with uncertainty 
        in time following a normal distribution
        """
        rand = np.random.normal(0, self.sigma)
        query_time = query_time + rand*timedelta(seconds=1)
        res = super()._search(query_time)
        return res
    
    def get_price_for_trader(self, query_time):
        return self._search(query_time)

    def get_delayed_price_for_amm(self, query_time):
        delayed_time = query_time - self.amm_delay
        return self._search(delayed_time)