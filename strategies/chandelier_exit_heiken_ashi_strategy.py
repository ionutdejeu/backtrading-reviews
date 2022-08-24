import base64
from io import BytesIO
import pandas as pd
import backtrader as bt
from backtrader import plot

import yfinance as yf


class ChandelierIndicatorDev(bt.Indicator):
    lines = ('CE', 'long_stop', 'short_stop','signal_line')
    params = (('stake', 100), ('period', 1), ('multip', 2), ("useClose", False),)
    plotinfo = dict(plot=True, subplot=False, plotorder=-100)
    plotlines = dict(
        CE=dict(ls='--', markersize=12.0),  # dashed line
        long_stop=dict(_samecolor=False,_plotskip=True),
        short_stop=dict(_samecolor=False,_plotskip=True),
        signal_line=dict(_samecolor=False,_plotvalue=False),
    )

    def __init__(self):

        self.highest = bt.indicators.Highest(self.datas[0].close, period=self.params.period)
        self.lowest = bt.indicators.Lowest(self.datas[0].close, period=self.params.period)

        self.org_atr = bt.ind.ATR(self.datas[0], period=self.params.period)
        self.atr = self.params.multip * self.org_atr

        self.long_stop = self.highest - self.atr
        self.short_stop = self.lowest + self.atr
        # initialise a dummy indicators, to be updated in next
        self.l.long_stop = bt.indicators.Max(0, 0)
        self.l.short_stop = bt.indicators.Max(0, 0)
        self.buy_signal = bt.indicators.Max(0, 0)
        self.sell_signal = bt.indicators.Max(0, 0)

        self.l.signal_line = bt.indicators.Max(0, 0)

    def next(self):
        if self.datas[0].close[-1] > self.l.long_stop[-1]:
            self.l.long_stop[0] = max(self.long_stop[0],self.l.long_stop[-1])
        else:
            self.l.long_stop[0] = self.long_stop[0]

        if self.datas[0].close[-1] < self.l.short_stop[-1]:
            self.l.short_stop[0] = min(self.short_stop[0],self.l.short_stop[-1])
        else:
            self.l.short_stop[0] = self.short_stop[0]


        #compute the direction to display the signal
        if self.datas[0].close > self.l.short_stop[-1]:
            self.l.signal_line[0] = self.l.long_stop[0]
            self.buy_signal[0] = 1
        elif self.datas[0].close < self.l.long_stop[-1]:
            self.l.signal_line[0] = self.l.short_stop[0]
            self.sell_signal[0] = 1
        else:
            self.l.signal_line[0] = self.l.signal_line[-1]


class ChandelierStrategyDev(bt.Strategy):

    params = (
        ('stake', 100),
        ('stoploss', 0.001),
        ('takeprofit', 0.002),
        ('profit_mult', 2),
        ('prdata', True),
        ('prtrade', True),
        ('prorder', True),
    )
    plotinfo = dict(subplot=True)

    def __init__(self):
        self.chandelier_exit = ChandelierIndicatorDev()
        self.lines.zlma = bt.ind.ZeroLagIndicator(self.datas[0], period=50,plotlinevalues=False)
        self.lines.ema_dy = bt.ind.ExponentialMovingAverage(self.datas[0], period=30,plotlinevalues=False)
        self.buy_signals = self.datas[0].close > self.zlma
        self.sell_signals = self.datas[0].close < self.zlma

    def next(self):
        print('a')


def getBacktestChart(runstrats):
    plotter = plot.Plot(use='Agg')
    backtestchart = ""
    for si, strat in enumerate(runstrats):
        rfig = plotter.plot(strat, figid=si * 100, numfigs=1)
        for f in rfig:
            buf = BytesIO()
            f.savefig(buf, bbox_inches='tight', format='png')
            imageSrc = base64.b64encode(buf.getvalue()).decode('ascii')
            backtestchart += f"{imageSrc}"

    return backtestchart


def backtest():
    # Back test the BuyChandelierStrategy with BackTrader
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ChandelierStrategyDev)
    yf_data = yf.download('AUDUSD=X', '2022-07-05', '2022-07-07', interval="15m")

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
        heikenAshi_close,
        heikenAshi_open,
        heikenAshi_high,
        heikenAshi_low]


    cerebro.adddata(bt.feeds.PandasData(dataname=frame))
    startValue = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % startValue)

    strats = cerebro.run(stdstats=False)

    endValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % endValue)
    a = getBacktestChart(strats)
    print(a)
    cerebro.plot(style="candle")
    return a

if __name__ == '__main__':
    backtest()

