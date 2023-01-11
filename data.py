import yfinance as yf
import pandas as pd



def current_price(symbol):
    data = yf.Ticker(symbol).history(period='1d', interval='1m')
    data_list = data.to_numpy().tolist()
    if len(data_list) == 0:
        return None
    return data_list[-1][3]

def get_balance_sheet(symbol):
    pass

def get_earnings(symbol):
    pass

# get info with the keys e.g. sector, ebitda, debt to equity etc...
def get_info(symbol, info_required):
    ticker = yf.Ticker(symbol)
    return ticker.info[info_required]

# how should we get the % change (maybe % change over a time interval like 5y, 1y, 6 months and 1 month)
def get_percentage_change(symbol):
    pass

print(get_info('BDBDBD', 'sector'))