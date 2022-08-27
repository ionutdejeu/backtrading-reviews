import pandas as pd

def SMA(array, n):
    """Exponential moving average"""
    return pd.Series(array).ewm(n).mean()
