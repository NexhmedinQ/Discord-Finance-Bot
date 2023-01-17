import yfinance as yf
import pandas as pd
from quickchart import QuickChart
from datetime import datetime, timedelta

def ticker_exists(symbol):
    data = yf.Ticker(symbol).history(period='1d', interval='1m')
    data_list = data.to_numpy().tolist()
    if len(data_list) == 0:
        return False
    return True

def current_price(symbol):
    data = yf.Ticker(symbol).history(period='1d', interval='1m')
    data_list = data.to_numpy().tolist()
    return data_list[-1][3]

def get_balance_sheet(symbol):
    print("calling5")
    ticker = yf.Ticker(symbol)
    bsheet = ticker.balance_sheet
    print(bsheet)
    headers = bsheet.index
    data_list = bsheet.to_numpy().tolist()
    ret = []
    for i, header in enumerate(headers):
        ret.append([header, int(data_list[i][0])])
    return ret
        

def get_earnings(symbol, is_quarterly):
    url = "https://quickchart.io/chart/render/sm-7f8c4fe9-3780-4fab-bbcc-b13efb8aa43a"
    ticker = yf.Ticker(symbol)
    if is_quarterly:
        earnings = ticker.quarterly_earnings
    else:
        earnings = ticker.earnings
    
    # get the graph labels
    x_labels = [str(label) for label in earnings.index.to_numpy().tolist()]
    labels = "labels=" + ','.join(x_labels)
    
    data = earnings.to_numpy().tolist()
    
    # get first dataset values(Revenue)
    data = earnings.to_numpy().tolist()
    revenue = [str(rev[0] / 1000000) for rev in data]
    data1 = "data1=" + ','.join(revenue)
    # get second dataset values(Earnings)
    earnings_list = [str(ear[1] / 1000000) for ear in data]
    data2 = "data2=" + ','.join(earnings_list)
    return f"{url}?{labels}&{data1}&{data2}"

# get info with the keys e.g. sector, ebitda, debt to equity etc...
def get_info(symbol, info_required):
    ticker = yf.Ticker(symbol)
    return ticker.info[info_required]

def get_news(symbols):
    datetime_yesterday = datetime.now() - timedelta(days=1)
    return_dict = {}
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        for one in news:
            if datetime.fromtimestamp(one['providerPublishTime']) < datetime_yesterday:
                break
            if one['uuid'] not in return_dict:
                return_dict[one['uuid']] = one
    return return_dict
