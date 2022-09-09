
import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy,Strategy
import yfinance as yf
from learning.stop_loss_tutorial import TrailingStopLoss
from trading_view.adx import ADX
from trading_view.ema import EMA
from trading_view.hlc3 import HLC3
from trading_view.rsi import RSI
from trading_view.sma import SMA
from trading_view.supertrend import SUPERTREND_UP, SUPERTREND_DOWN, SUPERTREND


class Strategy2SupertrendEMA(Strategy):
    n1 = 10
    n2 = 25
    ema_length = 50
    rsi_length = 14
    rsi_sma_length = 14

    def init(self):
        # In init() and in next() it is important to call the
        # super method to properly initialize the parent classes
        super().init()

        self.ema = self.I(EMA, self.data.Close, self.ema_length)
        self.daily_rsi = self.I(RSI, self.data.Close, self.rsi_length)
        self.rsi_sma = self.I(SMA,self.daily_rsi,self.rsi_sma_length)
        self.supertend_up = self.I(SUPERTREND,self.data,14,3)
        self.supertend_down = self.I(SUPERTREND_DOWN, self.data, 14, 3)

    def next(self):
        super().next()
        if self.position:
            pass
        else:
            pass




from backtesting import Backtest, Strategy
from backtesting.test import GOOG

if __name__ == '__main__':
    yf_data = yf.download('TSLA', '2021-01-01', '2022-08-28',interval="1h")

    frame = pd.DataFrame(yf_data)
    bt = Backtest(frame, Strategy2SupertrendEMA, commission=.002)
    bt.run()
    bt.plot()