from pnl_model import IPnLModel
from transaction import Transaction
from fees_model import ITransactFeesModel
from cex_market_info import CEXMarketInfo

from config import *



class Trader:
    def __init__(self, id: str):
        self.id = id
        self.fees_total: float = 0.0
        self.cum_pnl: pd.Series = pd.Series(dtype=float)
        self.history: list[Transaction] = []
    
    def on_new_trade(self, trade: pd.Series, fees_model: ITransactFeesModel, pnl_model: IPnLModel):
        self.history.append(Transaction(trade))
        fees = fees_model.calculate(self, trade)
        self.fees_total += fees
        tmp_pnl = self.get_current_pnl() + pnl_model.calculate(trade, fees)
        ts_datetime = pd.to_datetime(trade.timestamp, unit='s')
        self.cum_pnl.loc[ts_datetime] = tmp_pnl

    def get_current_pnl(self):
        return 0.0 if self.cum_pnl.empty else self.cum_pnl.iloc[-1]