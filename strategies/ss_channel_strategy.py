import datetime
import os.path
import sys
import pandas as pd
import backtrader as bt
from backtrader import plot

import yfinance as yf


class IndicatorDirection:
    Bullish = 1
    Bearish = -1

class ZeroLagExponentialMovingAverage(bt.Indicator):
    lines = ('ZLSMA',)

    def __init__(self):
        pass


class SSLChanelIndicator(bt.Indicator):
    lines = ('ssl_down','ssl_up',)
    params = (('stake', 100), ('period', 10),)
    plotinfo = dict(plot=True,subplot=False)
    plotlines = dict(
        CE=dict(ls='--', markersize=12.0),  # dashed line
        long_stop=dict(_samecolor=False),
        short_stop=dict(_samecolor=False),
    )

    def __init__(self):
        self.sma_low = bt.indicators.MovingAverageSimple(self.datas[0].low,period=self.params.period)
        self.sma_high = bt.indicators.MovingAverageSimple(self.datas[0].high,period=self.params.period)
        self.close_above_high = self.datas[0].close > self.sma_high
        self.close_below_low = self.datas[0].close < self.sma_low

        self.lines.ssl_up = self.sma_high

    def next(self):
        hlv = bt.NAN
        if self.close_below_low[0] > 0:
            hlv = 1
        elif self.close_above_high[0] > 0:
            hlv = -1
        self.lines.ssl_down[0] = self.sma_high[0] if hlv<0 else self.sma_low[0]
        self.lines.ssl_up[0] = self.sma_low[0] if hlv<0 else self.sma_high[0]

    def next2(self):
        hlv = bt.NAN
        if self.close_below_low[0] > 0:
            hlv = 1
        elif self.close_above_high[0] > 0:
            hlv = -1
        self.lines.ssl_down[0] = self.sma_high[0] if hlv<0 else self.sma_low[0]
        self.lines.ssl_up[0] = self.sma_low[0] if hlv<0 else self.sma_high[0]



def backtest():
    # Back test the BuyChandelierStrategy with BackTrader
    cerebro = bt.Cerebro()

    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.0035)
    #cerebro.addstrategy(ChandelierStrategyDev)
    cerebro.addindicator(SSLChanelIndicator)
    cerebro.addindicator(bt.ind.Stochastic)
    yf_data = yf.download('TSLA', '2022-06-01', '2022-06-03',interval="5m")

    frame = pd.DataFrame(yf_data)

    heikenAshi_close = [0] * len(frame)
    heikenAshi_open = [0] * len(frame)
    heikenAshi_high = [0] * len(frame)
    heikenAshi_low = [0] * len(frame)

    for index in range(len(frame)):
        heikenAshi_close[index] = 0.25 * (frame['Open'].values[index] +
                                          frame['Close'].values[index] +
                                          frame['High'].values[index] +
                                          frame['Low'].values[index])

        heikenAshi_open[index] = 0.5 * (frame['Open'].values[max(index - 1, 0)] +
                                        frame['Close'].values[max(index - 1, 0)])
        heikenAshi_high[index] = max(frame['High'].values[index], frame['Open'].values[index],
                                     frame['Close'].values[index])
        heikenAshi_low[index] = max(frame['Low'].values[index], frame['Open'].values[index],
                                    frame['Close'].values[index])

    frame['Close'], frame['Open'], frame['High'], frame['Low'] = [
        heikenAshi_close, heikenAshi_open, heikenAshi_high, heikenAshi_low]

    cerebro.adddata(bt.feeds.PandasData(dataname=frame))
    startValue = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % startValue)

    cerebro.run()

    endValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % endValue)

    cerebro.plot(style="candle")

if __name__ == '__main__':
    backtest()