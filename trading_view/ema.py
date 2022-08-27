import pandas as pd

def EMA(array, n):
    """Exponential moving average"""
    return pd.Series(array).ewm(n).mean()
