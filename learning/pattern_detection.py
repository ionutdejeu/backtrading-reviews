import backtesting as bt
import numpy as np
import pandas_ta as ta
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.test import SMA, GOOG
from backtesting.lib import TrailingStrategy, crossover

def RSI(array, n):
    """Relative strength index"""
    # Approximate; good enough
    gain = pd.Series(array).diff()
    loss = gain.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    rs = gain.ewm(n).mean() / loss.abs().ewm(n).mean()
    return 100 - 100 / (1 + rs)


class PatternDetectionStrategy(Strategy):

    def init(self):
        pass

    def next(self):
        if self.position:
            pass

        else:
            prise = self.data.Close[-1]
            self.buy(size=1, sl=prise - 10, tp=prise + 20)


def backtest():
    bt = Backtest(GOOG, PatternDetectionStrategy, cash=10_000)
    stat = bt.run()
    bt.plot()
    print(stat)


if __name__ == '__main__':
    backtest()

