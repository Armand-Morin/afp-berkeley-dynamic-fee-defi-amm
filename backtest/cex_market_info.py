from config import *

class CEXMarketInfo:
    def __init__(self, market_prices: pd.Series, amm_delay: timedelta):
        self.market_prices = market_prices
        self.amm_delay = amm_delay

    def _search(self, query_time):
        idx = self.market_prices.index.searchsorted(query_time)
        # Get the closest entry prior to the query datetime
        return self.market_prices.iloc[max(idx-1, 0)]

    def get_price_for_trader(self, query_time):
        return self._search(query_time)

    def get_delayed_price_for_amm(self, query_time):
        delayed_time = query_time - self.amm_delay
        return self._search(delayed_time)