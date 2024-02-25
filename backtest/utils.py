import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold


def zscore(series):
    return (series - series.mean()) / series.std()


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid(x, k=1, x0=0):
    return 1 / (1 + np.exp(-k * (x - x0)))


def adjusted_sigmoid(x, f_min=0.01, f_max=0.1, k=1, x0=0):
    return f_min + (f_max - f_min) * sigmoid(x, k=k, x0=x0)


def global_sigmoid(x, f_min, f_max, k=1, x0=0):
    if x > 0:
        return adjusted_sigmoid(x, f_min, f_max, k, x0)
    else:
        return adjusted_sigmoid(-x, f_min, f_max, k, x0)
    
    
def calculate_markout(d, v, f, p):
    m = d * v * (f - p)
    return m


# data_p1 = pd.read_pickle('data/Merged_CEX_DEX_v2_p1.pkl')
# data_p2 = pd.read_pickle('data/Merged_CEX_DEX_v2_p2.pkl')
# data_p3 = pd.read_pickle('data/Merged_CEX_DEX_v2_p3.pkl')

# data_p1['time'] = pd.to_datetime(data_p1['time'])
# data_p2['time'] = pd.to_datetime(data_p2['time'])
# data_p3['time'] = pd.to_datetime(data_p3['time'])

# data = pd.concat([data_p1, data_p2, data_p3])
# data = data.sort_values('time')