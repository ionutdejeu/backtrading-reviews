import backtesting as bt
import numpy as np
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG
from backtesting.lib import TrailingStrategy, crossover


class TrailingStopLoss(TrailingStrategy):

    _trailing_dollar_cost = 5

    def init(self):
        super().init()
        #super().set_trailing_sl(5)
        #self.set_atr_periods()

    def next(self):
        super().next()
        index = len(self.data) - 1
        for trade in self.trades:
            if trade.is_long:
                trade.sl = max(trade.sl or -np.inf,
                               self.data.Close[index] - self._trailing_dollar_cost)
            else:
                trade.sl = min(trade.sl or np.inf,
                               self.data.Close[index] + self._trailing_dollar_cost)



class StopLossStrategy(TrailingStopLoss):

    def init(self):
        pass

    def next(self):
        if self.position:
            pass
        else:
            prise = self.data.Close[-1]
            self.buy(size=1, sl=prise - 10, tp=prise + 20)



def backtest():
    bt = Backtest(GOOG, StopLossStrategy, cash=10_000)
    stat = bt.run()
    bt.plot()
    print(stat)


if __name__ == '__main__':
    backtest()
