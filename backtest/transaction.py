from config import *

class Transaction:
    def __init__(self, record: pd.Series):
        self.amount0 = record.amount0
        self.amount1 = record.amount1
        self.amountUSD = record.amountUSD
        self.timestamp = record.timestamp
        self.LVR = record.LVR
        self.record = record
