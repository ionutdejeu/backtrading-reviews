import pandas as pd
import backtrader as bt
import yfinance as yf


class CustomRSIIndicator(bt.Indicator):
    lines = ('STC',)
    params = (('stake', 100),('length', 12), ('slow_length', 50),('fast_length',26),)
    plotinfo = dict(plot=True)
    plotlines = dict(
        CE=dict(ls='--', markersize=12.0),  # dashed line
        long_stop=dict(_samecolor=False),
        short_stop=dict(_samecolor=False),
    )

    def __init__(self):
        self.costant_a = 0.5
        self.slow_ma = bt.indicators.ExponentialMovingAverage(self.datas[0].close,period=self.params.slow_length)
        self.fast_ma = bt.indicators.ExponentialMovingAverage(self.datas[0].close,period=self.params.fast_length)
        self.stoc = bt.indicators.Stochastic(self.datas[0].close,period=self.params.fast_length)

        self.ma_diff = self.fast_ma - self.slow_ma
        self.lowest = bt.indicators.Lowest(self.ma_diff,period=self.params.length)
        self.highest = bt.indicators.Highest(self.ma_diff,period=self.params.length)
        self.low_hi_diff = self.highest - self.lowest
        self.low_hi_diff_cmp = self.low_hi_diff > 0.0
        self.ddd = self.low_hi_diff_cmp*((self.ma_diff-self.lowest)/(self.highest*100))
        self.dddd = bt.indicators.Lowest(self.ddd,period=self.params.length)
        self.ddddd = bt.indicators.Highest(self.ddd,period=self.params.length)
        self.ddddd_cmp =  self.ddddd > 0
        self.dddddd = self.ddddd_cmp*((self.ddd - self.dddd)/(self.ddddd*100))
        self.lines.STC = bt.indicators.Max(0,0)
        self.lines.STC = self.lines.STC(-1) + self.costant_a * (self.dddddd - self.lines.STC(-1))





def backtest():
    # Back test the BuyChandelierStrategy with BackTrader
    cerebro = bt.Cerebro()

    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.0035)
    #cerebro.addstrategy(ChandelierStrategyDev)
    cerebro.addindicator(CustomRSIIndicator)
    yf_data = yf.download('TSLA', '2021-01-01', '2022-06-03')
                          #interval="5m")

    frame = pd.DataFrame(yf_data)

    cerebro.adddata(bt.feeds.PandasData(dataname=frame))
    startValue = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % startValue)

    cerebro.run()

    endValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % endValue)

    cerebro.plot(style="candle")

if __name__ == '__main__':
    backtest()