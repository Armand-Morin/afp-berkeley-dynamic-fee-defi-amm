import pandas as pd
import numpy as np
import plotly.express as px

from datetime import datetime, timedelta


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
        swap_price = abs(new_order.amount0 / new_order.amount1)
        swap_amount = abs(new_order.amountUSD / new_order.amount0)
        swap_direct = 1 if new_order.amount0 > 0 else -1
        return swap_direct * swap_amount * (mkt_price - swap_price) - fees



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

    
