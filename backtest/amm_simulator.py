from pnl_model import IPnLModel
from transaction import Transaction
from fees_model import ITransactFeesModel
from cex_market_info import CEXMarketInfo
from trader import Trader

from config import *

class AMMSimulator:
    """Simulation of automatic market maker transactions"""

    def __init__(self, market_info: CEXMarketInfo, fees_model: ITransactFeesModel,
                 pnl_model: IPnLModel, transactions_data: pd.DataFrame):
        """Initialize a new instance of the AMMSimulator class."""
        self.market_info = market_info
        self.fees_model = fees_model
        self.pnl_model = pnl_model
        self.raw_tx_data = transactions_data
        self.traders = dict()

        self.raw_tx_data.sort_values('timestamp')

    def _datetime_filter(self, start, end):
        return self.raw_tx_data[(self.raw_tx_data.index >= start) & (self.raw_tx_data.index <= end)]
    
    def _run_trader_records(self, trader_records: pd.DataFrame):
        trader_id = trader_records['sender'].iloc[0]
        print(f"Processing trader {trader_id}")
        trader = self.traders.setdefault(trader_id, Trader(trader_id))
        for idx, record in trader_records.iterrows():
            trade = Transaction(record)
            trader.on_new_trade(trade, self.fees_model, self.pnl_model)
        
    def replay(self, start_time=None, end_time=None):
        """Replay past transactions and summarize participants' PnL"""
        start_time = start_time or self.raw_tx_data.index[0]
        end_time = end_time or self.raw_tx_data.index[-1]

        #TODO: filter
        # records = self._datetime_filter(start_time, end_time)
        records = self.raw_tx_data
        records.groupby('sender').apply(self._run_trader_records)

        print(sorted([t.get_current_pnl() for t in self.traders.values()])[-10:])

    
