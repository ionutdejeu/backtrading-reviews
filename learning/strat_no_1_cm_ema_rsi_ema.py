import pandas as pd
from backtesting.lib import SignalStrategy, TrailingStrategy,Strategy
import yfinance as yf
from learning.stop_loss_tutorial import TrailingStopLoss
from trading_view.adx import ADX
from trading_view.ema import EMA
from trading_view.hlc3 import HLC3
from trading_view.rsi import RSI
from trading_view.sma import SMA


def CONSTANT(array):
    """Exponential moving average"""
    return pd.Series(array)



class SmaCross(Strategy):
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
        self.rsi_sma_below_60 = self.I(CONSTANT,(pd.Series(self.rsi_sma) < 60).astype(int).diff().fillna(0))
        self.hlc3 = self.I(HLC3,self.data)
        self.adx = self.I(ADX,self.data,7)
        self.adx_avg = pd.Series(self.adx).ewm(14).mean()

    def next(self):
        super().next()
        if self.position:
            if self.rsi_sma_below_60[-1] > 0:
                self.position.close()
        else:

            curr_rsi_sma = self.daily_rsi[-1]
            curr_ema = self.ema[-1]
            price = self.data.Low[-1]
            curr_adx_avg = self.adx_avg
            #long condition
            if curr_ema < price and curr_rsi_sma > 50 and self.adx[-1]>25:
                try:
                    sl_price = curr_ema
                    tp_price1 = price + abs(price-curr_ema)*3
                    tp_price2 = price * 1.05
                    tp_price = tp_price1 if tp_price1 > tp_price2 else tp_price2

                    self.buy(size=1, sl=sl_price,tp=tp_price2)


                except Exception as e:
                    print(e)
                    pass


from backtesting import Backtest, Strategy
from backtesting.test import GOOG

if __name__ == '__main__':
    yf_data = yf.download('TSLA', '2021-01-01', '2022-08-28',interval="1h")

    frame = pd.DataFrame(yf_data)
    bt = Backtest(frame, SmaCross, commission=.002)
    bt.run()
    bt.plot()

