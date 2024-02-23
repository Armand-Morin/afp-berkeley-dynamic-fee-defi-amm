
from cex_market_info import ICEXMarketInfo
from transaction import Transaction

from config import *


class IPnLModel:
    """Trader's PnL calculation interface"""
    def __init__(self, cex_market_info: ICEXMarketInfo):
        self.cex_market_info = cex_market_info

    def calculate(self, new_order: Transaction, fees: int):
        raise NotImplementedError

class SimplePnLModel(IPnLModel):
    def calculate(self, new_order: Transaction, fees: int):
        query_time = pd.to_datetime(new_order.timestamp, unit='s')
        mkt_price = self.cex_market_info.get_price_for_trader(query_time)
        swap_price = abs(new_order.amount0 / new_order.amount1)
        swap_amount = abs(new_order.amountUSD / new_order.amount0)
        swap_direct = 1 if new_order.amount0 > 0 else -1
        return swap_direct * swap_amount * (mkt_price - swap_price) - fees