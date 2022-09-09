import pandas as pd


def DEMA(array, n):
    """Exponential moving average"""
    # Calculate the Exponential Moving Average for some time_period (in days)
    EMA = pd.Series(array).ewm(span=n, adjust=False).mean()
    # Calculate the DEMA
    DEMA = 2 * EMA - EMA.ewm(span=n, adjust=False).mean()
    return DEMA
