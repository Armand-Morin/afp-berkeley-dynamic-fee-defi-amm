from market import MarketInfo, Transaction
from trader import Trader
import numpy as np

# methodology:
# Take a rolling windows of the past 1 million tx for instance
# Perform all the signle trades analysis, in term of pnl anf LVR percent
# Aggregate the metrics to get the trader perfs 
# Charge the fee per trader

def zscore(series):
    return (series - series.mean()) / series.std()


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
        
    def quote_fee():
        pass
    

# Define a simple fees model
class SimpleTransactFeesModel(ITransactFeesModel):
    def calculate(self, trader: Trader, new_order: Transaction):
        fees_factor = max(0, trader.get_current_pnl()) * 5*10**(-3)
        return new_order.amount0 * fees_factor


    def calculate(self, trader, new_order: Transaction):
        data = pd.read_pickle('Merged_CEX_DEX_v2_p1.pkl')
        
        data['LVR_nbtoken'] = data['LVR']/data['price_dex']
        data['LVR_pnl_percent'] = (np.abs(data['LVR_clean']*data['amountUSD'])-data['tcost_usd'])*100/data['amountUSD']
        data['LVR_zscore'] = zscore(data['LVR'])
        
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
        
        please = pd.DataFrame.from_dict(merged_dict, orient='index', columns=['fees'])
        please = please.reset_index().rename(columns={'index': 'address'}).sort_values(by='fees', ascending=False)

        merged_data = data.merge(please.rename(columns={'fees' : 'f1'}), left_on='sender', how='left', right_on='address')
        merged_data = merged_data.merge(please.rename(columns={'fees' : 'f2'}), left_on='origin', how='left', right_on='address')
        merged_data = merged_data.merge(please.rename(columns={'fees' : 'f3'}), left_on='recipient', how='left', right_on='address')

        merged_data[['f1', 'f2', 'f3']] = merged_data[['f1', 'f2', 'f3']].fillna(0).clip(lower=0.05)

        merged_data['mean_fee'] = merged_data[['f1', 'f2', 'f3']].mean(axis=1) 
        #merged_data['max_fee']  = merged_data[['f1', 'f2', 'f3']].max(axis=1) 

        merged_data = merged_data.drop(columns=['address_x', 'address_y', 'address', 'f1', 'f2', 'f3']).fillna(0.5)

        (merged_data['mean_fee'] * merged_data['amountUSD']/100).sum()
        
        return merged_dict


