import pandas as pd
import numpy as np

from trading_view.atr import ATR
from trading_view.hl2 import HL2


from trading_view.atr import ATR
from trading_view.hl2 import HL2


def SUPERTREND_DOWN(data, n, multiplier=3):
    df = pd.DataFrame()
    df['close'] = data.Close
    df['atr'] = ATR(data, n)
    df['src'] = HL2(data)
    df['down'] = df['src'] + multiplier * df['atr']
    return df['down'].rolling(n).min()


def SUPERTREND_MID(data, n, multiplier=3,atr:pd.Series=None):
    df = pd.DataFrame()
    df['close'] = data.Close
    df['atr'] = ATR(data, n)
    df['src'] = HL2(data)
    df['up'] = df['src'] - multiplier * df['atr']
    df['down'] = df['src'] + multiplier * df['atr']

    return (df['src'] - multiplier * df['atr']).rolling(n).min()


def SUPERTREND_UP(data, n, multiplier=3):
    df = pd.DataFrame()
    df['close'] = data.Close
    df['atr'] = ATR(data, n)
    df['src'] = HL2(data)
    df['up'] = df['src'] - multiplier * df['atr']
    df['res'] = df['src'] - multiplier * df['atr']
    return df['up'].rolling(n).max()



def SUPERTREND(data, n, multiplier=3):
    df = pd.DataFrame()
    df['close'] = data.Close
    df['atr'] = ATR(data, n)
    df['src'] = HL2(data)
    df['up'] = df['src'] - multiplier * df['atr']
    df['down'] = df['src'] + multiplier * df['atr']
    df['supertrend'] = np.nan
    df['buy_signal'] = np.nan
    df['sell_signal'] = np.nan
    df['long_stop'] = df['close']
    df['long_stop'] = df['long_stop'].rolling(n).max()
    df['short_stop'] = df['close']
    df['short_stop'] = df['short_stop'].rolling(n).min()

    return pd.DataFrame([df['short_stop']])

