from market import MarketInfo, Transaction


class ITransactFeesModel:
    """Transaction fees calculation interface"""
    def __init__(self, market_info: MarketInfo):
        self.market_info = market_info

    def calculate(self, trader, new_order: Transaction):
        pass

