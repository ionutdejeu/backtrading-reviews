from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.indicators as btind
import yfinance as yf
import pandas as pd

from api.engine.chandelier_exit_heiken_ashi_strategy import getBacktestChart


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

    def __init__(self):
        self.bbands = self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
        self.order_dict = {}
        self.buy_sig = btind.CrossOver(self.data, self.bbands.line2)
        self.sell_sig = btind.CrossOver(self.bbands.line0, self.data)
        self.trades = 0
        self.order = None

    def start(self):
        self.trades = 0

    def next(self):
        if self.position:
            return
        else:
            if self.buy_sig > 0:
                # import ipdb; ipdb.set_trace()
                self.buy(exectype=bt.Order.Market)
                self.last_sig_price = self.data.close[0]
                self.trades += 1
            elif self.sell_sig > 0:
                self.sell(exextype=bt.Order.Market)
                self.trades += 1

                if self.p.prdata:
                    print(','.join(str(x) for x in
                    ['DATA', 'OPEN',
                        self.data.datetime.date().isoformat(),
                        self.data.close[0],
                        self.buy_sig[0]]))


    def notify_order(self, order):
        # import ipdb; ipdb.set_trace()
        if order.status in [order.Margin, order.Rejected]:
            pass
        elif order.status == order.Cancelled:
            if self.p.prorder:
                print(','.join(map(str, [
                    'CANCELL', order.info['OCO'], order.ref,
                    self.data.num2date(order.executed.dt).date().isoformat(),
                    order.executed.price,
                    order.executed.size,
                    order.executed.comm,
                ]
                )))
        elif order.status == order.Completed:
            if 'name' in order.info:
                self.broker.cancel(self.order_dict[order.ref])
                self.order = None
                if self.p.prorder:
                    print("%s: %s %s %.2f %.2f %.2f" %
                        (order.info['name'], order.ref,
                        self.data.num2date(order.executed.dt).date().isoformat(),
                        order.executed.price,
                        order.executed.size,
                        order.executed.comm))
            else:
                if order.isbuy():
                    stop_loss = order.executed.price*(1.0 - (self.p.stoploss))
                    take_profit = order.executed.price*(1.0 + self.p.profit_mult*(self.p.stoploss))

                    sl_ord = self.sell(exectype=bt.Order.Stop,
                                       price=stop_loss)
                    sl_ord.addinfo(name="Stop")

                    tkp_ord = self.sell(exectype=bt.Order.Limit,
                                        price=take_profit)
                    tkp_ord.addinfo(name="Prof")

                    self.order_dict[sl_ord.ref] = tkp_ord
                    self.order_dict[tkp_ord.ref] = sl_ord

                    if self.p.prorder:
                        print("SignalPrice: %.2f Buy: %.2f, Stop: %.2f, Prof: %.2f"
                              % (self.last_sig_price,
                                 order.executed.price,
                                 stop_loss,
                                 take_profit))

                elif order.issell():
                    stop_loss = order.executed.price*(1.0 + (self.p.stoploss))
                    take_profit = order.executed.price*(1.0 - 3*(self.p.stoploss))

                    sl_ord = self.buy(exectype=bt.Order.Stop,
                                      price=stop_loss)
                    sl_ord.addinfo(name="Stop")

                    tkp_ord = self.buy(exectype=bt.Order.Limit,
                                        price=take_profit)
                    tkp_ord.addinfo(name="Prof")

                    self.order_dict[sl_ord.ref] = tkp_ord
                    self.order_dict[tkp_ord.ref] = sl_ord

                if self.p.prorder:
                    print("Open: %s %s %.2f %.2f %.2f" %
                        (order.ref,
                         self.data.num2date(order.executed.dt).date().isoformat(),
                        order.executed.price,
                        order.executed.size,
                        order.executed.comm))

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
    cerebro.addstrategy(BBands)
    yf_data = yf.download('AUDUSD=X', '2022-07-05', '2022-07-07', interval="15m")

    frame = pd.DataFrame(yf_data)

    cerebro.adddata(bt.feeds.PandasData(dataname=frame))
    startValue = cerebro.broker.getvalue()
    print('Starting Portfolio Value: %.2f' % startValue)

    strats = cerebro.run(stdstats=False)

    endValue = cerebro.broker.getvalue()
    print('Final Portfolio Value: %.2f' % endValue)
    a = getBacktestChart(strats)

    cerebro.plot(style="candle")
    return a

if __name__ == '__main__':
    backtest()
