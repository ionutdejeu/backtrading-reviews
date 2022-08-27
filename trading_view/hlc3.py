import pandas as pd

# Using Dataframe.apply() to apply function to every row
def compute_hlc3(row):
   return (row['High']+row['Low']+row["Close"])/3

def HLC3(data):
    """Exponential moving average"""
    res= (data.High + data.Low + data.Close) / 3
    return res
