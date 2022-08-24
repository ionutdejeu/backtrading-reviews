import base64
from io import BytesIO
import pandas as pd
import backtesting as bt
from backtesting import _plotting

class SuperTrendIndicator(bt.Indicator):
    lines = ('CE', 'long_stop', 'short_stop','signal_line')
    params = (('stake', 100), ('period', 1), ('multip', 3), ("useClose", False),)
    plotinfo = dict(plot=True, subplot=False, plotorder=-100)
    plotlines = dict(
        CE=dict(ls='--', markersize=12.0),  # dashed line
        long_stop=dict(_samecolor=False,_plotskip=True),
        short_stop=dict(_samecolor=False,_plotskip=True),
        signal_line=dict(_samecolor=False,_plotvalue=False),
    )

    def __init__(self):

        self.source = (self.datas[0].high + self.datas[0].low)/2
        self.org_atr = bt.ind.ATR(self.datas[0], period=self.params.period)
        self.atr = self.params.multip * self.org_atr

        self.long_stop = self.source - self.atr
        self.short_stop = self.source + self.atr
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
        self.super_trent = SuperTrendIndicator()
        self.lines.zlma = bt.ind.ZeroLagIndicator(self.datas[0], period=50,plotlinevalues=False)
        self.lines.ema_dy = bt.ind.ExponentialMovingAverage(self.datas[0], period=30,plotlinevalues=False)
        self.buy_signals = self.datas[0].close > self.zlma
        self.sell_signals = self.datas[0].close < self.zlma

    def next(self):
        pass

    def prepare_buy_message(self):
        return {
            "action": "buy",
        }
    def prepare_sell_message(self):
        return {
            "action": "sell",
        }
    def should_notify_clients(self):
        last_value = self.super_trent.buy_signal.array[-1]
        print(last_value)
        if last_value == 1:
            return self.prepare_buy_message()
        last_value = self.super_trent.sell_signal.array[-1]
        print(last_value)
        if last_value == 1:
            return self.prepare_sell_message()
        return None

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


def backtest(symbol:str='XLM-USD'):
    # Back test the BuyChandelierStrategy with BackTrader
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ChandelierStrategyDev)
    yf_data = yf.download(symbol, '2022-07-12', '2022-07-13', interval="15m")
    frame = pd.DataFrame(yf_data)
    cerebro.adddata(bt.feeds.PandasData(dataname=frame))
    strats = cerebro.run(stdstats=False)
    should_notify = strats[0].should_notify_clients()
    cerebro.plot(style="candle")
    img_content = getBacktestChart(strats)
    return should_notify,img_content

if __name__ == '__main__':
    backtest()

