from cex_market_info import ICEXMarketInfo
from transaction import Transaction

from config import *


class ITransactFeesModel:
    """Transaction fees calculation interface"""
    def __init__(self, cex_market_info: ICEXMarketInfo):
        self.cex_market_info = cex_market_info

    def calculate(self, trader, new_order: Transaction):
        raise NotImplementedError


class SimpleTransactFeesModel(ITransactFeesModel):
    """Simple fees model based on cumulative PnL"""
    def calculate(self, trader, new_order: Transaction):
        fees_factor = max(0, trader.get_current_pnl()) * 5*10**(-3)
        return new_order.amount0 * fees_factor