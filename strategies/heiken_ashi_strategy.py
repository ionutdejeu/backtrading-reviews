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


class ChandelierIndicatorDev(bt.Indicator):
    #alias = ('CE', 'ChandelierExit',)
    lines = ('CE','long_stop','short_stop',)
    params = (('stake', 100), ('period', 1), ('multip', 2), ("useClose", False),)
    plotinfo = dict(plot=True,subplot=False,plotorder=-100)
    plotlines = dict(
        CE=dict(ls='--', markersize=12.0),  # dashed line
        long_stop=dict(_samecolor=False),
        short_stop=dict(_samecolor=False),
    )

    def __init__(self):


        self.highest = bt.indicators.Highest(self.datas[0].close,period=self.params.period)
        self.lowest = bt.ind.Lowest(self.datas[0].close,period=self.params.period)

        atr = bt.ind.ATR(self.datas[0], period=self.params.period)
        self.atr = atr * self.params.multip
        self.l.long_stop = self.highest - self.atr
        self.l.short_stop = self.lowest + self.atr
        self.dir_bullish = self.datas[0].close > self.l.short_stop(-1)
        self.dir_bearish = self.datas[0].close < self.l.long_stop(-1)
        self.buy_signal = self.datas[0].close < self.l.long_stop(-1)
        self.sell_signal = self.datas[0].close < self.l.long_stop(-1)


    def next(self):

        long_stop_cond = self.datas[0].close[-1] > self.l.long_stop[0]
        short_stop_cond = self.datas[0].close[-1] < self.l.short_stop[0]
        long_stop_value = max(self.l.long_stop[0], self.l.long_stop[0]) if long_stop_cond else \
           self.l.long_stop[0]
        short_stop_value = min(self.l.short_stop[0], self.l.short_stop[0]) if short_stop_cond else \
            self.l.short_stop[0]
        long_stop_plot_cond = self.datas[0].close[0] > self.l.short_stop[-1]
        short_stop_plot_cond = self.datas[0].close[0] < self.l.long_stop[-1]
        self.l.CE[0] = self.l.CE[-1]
        print(f'stop:{short_stop_plot_cond} long:{long_stop_plot_cond}')
        if short_stop_plot_cond:
            print('a')
        if self.dir_bullish[0]:
           self.l.CE[0] = long_stop_value
        if self.dir_bearish[0]:
           self.l.CE[0] = short_stop_value

        self.buy_signal[0] = 0
        self.buy_signal[0] = self.buy_signal[-1] > 0 or (self.dir_bullish[0] > 0 and self.buy_signal[-1] == 0)
        self.sell_signal[0] = self.sell_signal[-1] > 0 or (self.dir_bearish[0] > 0 and self.sell_signal[-1] == 0)



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
        self.sizer.setsizing(self.params.stake)
        # Keep a reference to the "close" line in the data[0] dataseries
        self.chandelier_exit = ChandelierIndicatorDev()
        self.lines.zlma = bt.ind.ZeroLagIndicator(self.datas[0], period=50)
        self.lines.ema_dy = bt.ind.ExponentialMovingAverage(self.datas[0], period=30)
        self.lines.ema_dy = bt.ind.MovingAverageSimple(self.datas[0], period=30)

        self.trades = 0
        self.order = None
        self.order_dict = {}

    def start(self):
        self.trades = 0

    def notify_order(self, order):
        # import ipdb; ipdb.set_trace()
        if not order.status == order.Completed:
            return  # discard any other notification

        if not self.position:  # we left the market
            print("SL hit")
            print(f'SELL@price: {order.executed.price}, exectype = {bt.Order.ExecTypes[order.exectype]}')
            self.order = None
            return

        print(f'SELL @price: {order.executed.price}, exectype = {bt.Order.ExecTypes[order.exectype]}')
        stop_loss_price = order.executed.price * (1.0 - self.p.stoploss)
        self.sell(exectype=bt.Order.Stop, price=stop_loss_price)

        print(f'SELL @price: {order.executed.price}, exectype = {bt.Order.ExecTypes[order.exectype]}')
        take_profit_price = order.executed.price * (1.0 + self.p.takeprofit)
        self.sell(exectype=bt.Order.Sell, price=take_profit_price)

    def next(self):
        price_above_zlma = self.datas[0].close[0] > self.zlma[0]
        price_below_zlma = self.datas[0].close[0] < self.zlma[0]
        shouldBuy = self.chandelier_exit.buy_signal[0] and price_above_zlma
        shouldSell = self.chandelier_exit.sell_signal[0] and price_below_zlma

        if shouldBuy and not self.order:
            self.order = self.buy(exectype=bt.Order.Market)
            self.trades += 1
            if self.p.prdata:
                print(','.join(str(x) for x in
                               ['DATA', 'OPEN',
                                self.data.datetime.date().isoformat(),
                                self.data.close[0],
                                0]))



    def notify_trade(self, trade):
        # import ipdb; ipdb.set_trace()
        if self.p.prtrade:
            if trade.isclosed:
                print('TRADE PROFIT, GROSS %.2f, NET %.2f' %
                      (trade.pnl, trade.pnlcomm))
            elif trade.justopened:
                print(','.join(map(str, [
                    'TRADE', 'OPEN',
                    self.data.num2date(trade.dtopen).date().isoformat(),
                    trade.value,
                    trade.pnl,
                    trade.commission,
                ]
                                   )))

    def stop(self):
        print('(Stop Loss Pct: %2f, S/P Multiplier: %2f) Ending Value %.2f (Num Trades: %d)' %
              (self.params.stoploss, self.params.profit_mult, self.broker.getvalue(), self.trades))


def backtest():
    # Back test the BuyChandelierStrategy with BackTrader
    cerebro = bt.Cerebro()

    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.0035)
    cerebro.addstrategy(ChandelierStrategyDev)
    #cerebro.addindicator(ChandelierIndicatorDev)
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