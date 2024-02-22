from market import MarketInfo, Transaction
import numpy as np

# methodology:
# Take a rolling windows of the past 1 million tx for instance
# Perform all the signle trades analysis, in term of pnl anf LVR percent
# Aggregate the metrics to get the trader perfs 
# Charge the fee per trader



def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def fee_pnl(LVR_pnl_percent):
    # output is in 100%
    coef = 1
    return sigmoid(LVR_pnl_percent / 250) * coef

def fee_base(LVR_zscore):
    # output is in 100%
    base_pool_fee = 0.05
    coef = 1.03
    return coef * sigmoid(base_pool_fee + LVR_zscore * 0.03)


class ITransactFeesModel:
    """Transaction fees calculation interface"""
    def __init__(self, market_info: MarketInfo):
        self.market_info = market_info

    def calculate(self, trader, new_order: Transaction):
        
        agg_sender = data[['LVR_pnl_percent', 'LVR_zscore', 'sender']].groupby('sender').sum()
        agg_origin = data[['LVR_pnl_percent', 'LVR_zscore', 'origin']].groupby('origin').sum()
        agg_recipient = data[['LVR_pnl_percent', 'LVR_zscore', 'recipient']].groupby('recipient').sum()

        dico_percent = {}
        dico_zscore = {}

        for df in [agg_sender, agg_origin, agg_recipient]:
            for address, lvr_percent, lvr_zscore in zip(df.index, df['LVR_pnl_percent'], df['LVR_zscore']):
                if address in dico_percent:
                    dico_percent[address] += lvr_percent
                    dico_zscore[address] += lvr_zscore
                else:
                    dico_percent[address] = lvr_percent
                    dico_zscore[address] = lvr_zscore


        # filter addresses trading with positive LVR return 
        dic_base_fee = {address: fee_base(LVR_zscore) for address, LVR_zscore in dico_zscore.items() if LVR_zscore > 0}

        dic_fee       = {address: fee_pnl(LVR_pnl_percent) for address, LVR_pnl_percent in dico_percent.items() if LVR_pnl_percent > 0 }

        merged_dict = {key: dic_fee.get(key, 0) + dic_base_fee.get(key, 0) for key in set(dic_fee) | set(dic_base_fee)}
        
        return merged_dict
    
    
    
    





