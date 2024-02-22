from cex_market_info import CEXMarketInfo
from transaction import Transaction
from trader import Trader
from config import *


class ITransactFeesModel:
    """Transaction fees calculation interface"""
    def __init__(self, market_info: CEXMarketInfo):
        self.market_info = market_info

    def calculate(self, trader, new_order: Transaction):
        pass

class SimpleTransactFeesModel(ITransactFeesModel):
    """Simple fees model based on cumulative PnL"""
    def calculate(self, trader: Trader, new_order: Transaction):
        fees_factor = max(0, trader.get_current_pnl()) * 5*10**(-3)
        return new_order.amount0 * fees_factor