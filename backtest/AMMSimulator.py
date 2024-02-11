import pandas as pd
import numpy as np
import plotly.express as px

from datetime import datetime, timedelta

class Transaction:
    def __init__(self, record: pd.Series):
        self.amount0 = record.amount0
        self.amount1 = record.amount1
        self.timestamp = record.timestamp
        self.price = record.price

class MarketInfo:
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

class ITransactFeesModel:
    """Transaction fees calculation interface"""
    def __init__(self, market_info: MarketInfo):
        self.market_info = market_info

    def calculate(self, trader, new_order: Transaction):
        pass

class IPnLModel:
    """Trader's PnL calculation interface"""
    def __init__(self, market_info: MarketInfo):
        self.market_info = market_info

    def calculate(self, new_order: Transaction, fees: int):
        pass

class SimplePnLModel(IPnLModel):
    def calculate(self, new_order: Transaction, fees: int):
        query_time = pd.to_datetime(new_order.timestamp, unit='s')
        mkt_price = self.market_info.get_price_for_trader(query_time)
        # print("JOey ", new_order.amount0, (mkt_price, new_order.price), fees)
        # return new_order.amount0 * (mkt_price - new_order.price) - fees
        return 1

class Trader:
    def __init__(self, id: str):
        self.id = id
        self.cum_pnl: list[float] = [0.0]
        self.history: list[Transaction] = []
    
    def on_new_trade(self, trade: pd.Series, fees_model: ITransactFeesModel, pnl_model: IPnLModel):
        self.history.append(Transaction(trade))
        fees = fees_model.calculate(self, trade)
        tmp_pnl = self.cum_pnl[-1] + pnl_model.calculate(trade, fees)
        self.cum_pnl.append(tmp_pnl)

    def get_current_pnl(self):
        return self.cum_pnl[-1]

class AMMSimulator:
    """Simulation of automatic market maker transactions"""

    def __init__(self, market_info: MarketInfo, fees_model: ITransactFeesModel,
                 pnl_model: IPnLModel, transactions_data: pd.DataFrame):
        """Initialize a new instance of the AMMSimulator class."""
        self.market_info = market_info
        self.fees_model = fees_model
        self.pnl_model = pnl_model
        self.raw_tx_data = transactions_data
        self.traders = dict()

        self.raw_tx_data.sort_values('timestamp')

    def _datetime_filter(self, start, end):
        return (self.raw_tx_data.index >= start) & (self.raw_tx_data.index <= end)
    
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

        records = self.raw_tx_data
        # print(self.raw_tx_data.info())
        records.groupby('sender').apply(self._run_trader_records)

        print(sorted([t.get_current_pnl() for t in self.traders.values()])[-10:])


class SimpleTransactFeesModel(ITransactFeesModel):
    def calculate(self, trader, new_order: Transaction):
        fees_factor = max(0, trader.get_current_pnl()*0.002)
        # print(f'model: {new_order.amount0}, {fees_factor}, {new_order.amount0 * fees_factor}!!')
        # return new_order.amount0 * fees_factor
        return 0
    
