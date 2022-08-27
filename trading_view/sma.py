import pandas as pd

def SMA(array, n):
    """Exponential moving average"""
    res= pd.Series(array).ewm(n).mean()
    return res