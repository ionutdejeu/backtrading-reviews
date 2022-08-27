import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy

from trading_view.ema import EMA
from trading_view.hlc3 import HLC3
from trading_view.rsi import RSI
from trading_view.sma import SMA

class SmaCross(SignalStrategy,
               TrailingStrategy):
    n1 = 10
    n2 = 25
    ema_length = 34
    rsi_length = 14
    rsi_sma_length = 14


    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()


        self.ema = self.I(EMA, self.data.Close, self.ema_length)
        self.daily_rsi = self.I(RSI, self.data.Close, self.rsi_length)
        rsi_sma = self.I(SMA,self.daily_rsi,self.rsi_sma_length)
        self.hlc3 = self.I(HLC3,self.data)


        #signal for the RSI ema
        signal_rsi_ema = (pd.Series(rsi_sma) > 50)
        # Where sma1 crosses sma2 upwards. Diff gives us [-1,0, *1*]
        signal_ema = (pd.Series(self.ema) > self.hlc3).astype(int).diff().fillna(0)
        signal_ema = signal_ema.replace(-1, 0)  # Upwards/long only

        # Use 95% of available liquidity (at the time) on each order.
        # (Leaving a value of 1. would instead buy a single share.)
        entry_size = signal_ema * .95

        # Set order entry sizes using the method provided by
        # `SignalStrategy`. See the docs.
        self.set_signal(entry_size=entry_size)

        # Set trailing stop-loss to 2x ATR using
        # the method provided by `TrailingStrategy`
        self.set_trailing_sl(2)


from backtesting import Backtest
from backtesting.test import GOOG

if __name__ == '__main__':
    bt = Backtest(GOOG, SmaCross, commission=.002)
    bt.run()
    bt.plot()