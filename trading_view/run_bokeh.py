import bokeh.io
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource, Column

from sockstats import StockDataFrame
from visualisation import plot_stock_price, plot_sma, plot_macd, plot_rsi, plot_obv, widget_symbols, widget_show_text

intro_text = "Data is current, courtesy of https://iextrading.com/"

warning_text = "Dropbox is slow to load, please be patience (7000+ stocks)."

stock = ColumnDataSource(
    data=dict(date=[], open=[], close=[], high=[], low=[], OBV=[], SMA_5=[], SMA_10=[], SMA_50=[], SMA_100=[], macd=[],
              macd_histogram=[], macd_signal=[], close_line=[], rsi_15=[], zeros=[]))




def update():

    # Test getting 6m chart
    yf_data = yf.download('TSLA', '2022-03-03', '2022-08-28')

    data_temp = pd.DataFrame(yf_data)
    df_temp = data_temp.copy()
    df_temp['date'] = df_temp.index
    df_temp['close'] = df_temp['Close']
    df_temp['open'] = df_temp['Open']
    df_temp['high'] = df_temp['High']
    df_temp['low'] = df_temp['Low']
    df_temp['volume'] = df_temp['Volume']

    del df_temp['Close'],df_temp['Open'],df_temp['High'],df_temp['Low'],df_temp['Volume'],df_temp['Adj Close']

    stock_data = StockDataFrame(df_temp.copy())

    data = pd.DataFrame(df_temp)
    # Adding indicators
    # Smoothed close price line
    # data['close_line'] = savgol_filter(stock.data['close'], 9, 3)
    data['rsi_15'] = stock_data['rsi_15']
    data['bolling_upper'] = stock_data['boll_ub']
    data['bolling_lower'] = stock_data['boll_lb']
    data['macd'] = stock_data['macd']
    data['macd_signal'] = stock_data['macds']
    data['macd_histogram'] = stock_data['macdh']
    # Moving averages
    data['SMA_5'] = stock_data['close_5_sma']
    data['SMA_10'] = stock_data['close_10_sma']
    data['SMA_50'] = stock_data['close_50_sma']
    data['SMA_100'] = stock_data['close_100_sma']
    # On-Balance Volume (OBV)
    obv = list()
    for today in range(0, len(stock_data)):
        if today == 0:
            obv.append(0)
            continue
        # Today price higher than yesterday
        if stock_data.close.iloc[today] > stock_data.close.iloc[today - 1]:
            obv.append(obv[today - 1] + stock_data.volume.iloc[today])
            continue
        # Today price lower than yesterday
        if stock_data.close.iloc[today] < stock_data.close.iloc[today - 1]:
            obv.append(obv[today - 1] - stock_data.volume.iloc[today])
            continue
        # Today price same as yesterday
        obv.append(obv[today - 1])
    data['OBV'] = np.array(obv)
    data['zeros'] = np.zeros(len(obv))

    stock.data = stock.from_df(data)


elements = list()

update()

p_stock = plot_stock_price(stock)

p_sma = plot_sma(stock)
p_sma.x_range = p_stock.x_range

p_macd = plot_macd(stock)
p_macd.x_range = p_stock.x_range

p_rsi = plot_rsi(stock)
p_rsi.x_range = p_stock.x_range

p_obv = plot_obv(stock)
p_obv.x_range = p_stock.x_range

elements.append(Column(widget_show_text(intro_text)))
elements.append(Column(widget_show_text(warning_text)))
elements.append(p_stock)
elements.append(p_sma)
elements.append(p_macd)
elements.append(p_rsi)
elements.append(p_obv)

curdoc().add_root(column(elements))
curdoc().title = 'Bokeh stocks data'


