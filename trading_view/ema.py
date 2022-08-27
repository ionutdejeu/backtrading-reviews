import pandas as pd

def EMA(array, n):
    """Simple moving average"""
    return pd.Series(array).rolling(n).mean()
