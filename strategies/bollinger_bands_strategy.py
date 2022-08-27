import backtesting as bt
import pandas_ta as ta
from backtesting import Backtest
from backtesting.test import SMA, GOOG


def indicator(data):
    bbands = ta.bbands(close=data.Close.s,std=1)
    print(bbands)
    return bbands.to_numpy()

class BBands(bt.Strategy):
    params = (
        ('stoploss', 0.001),
        ('profit_mult', 2),
        ('prdata', False),
        ('prtrade', False),
        ('prorder', False),
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
    )

    def init(self):
        self.bbands = self.boll = self.I(indicator,self.data)

    def start(self):
        pass

    def next(self):
       pass

    def notify_order(self, order):
         pass

    def notify_trade(self, trade):
        pass

    def stop(self):
        pass


def backtest():
    bt= Backtest(GOOG,BBands,cash=10_000)
    stat = bt.run()
    bt.plot()
    print(stat)
if __name__ == '__main__':
    backtest()
