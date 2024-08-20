import pandas as pd
import numpy as np
from datetime import datetime, timedelta

#relative_price_factor
current_date = datetime.strptime('20240621', '%Y%m%d')

def concatenate_data(current_time):
    start_date = current_time - timedelta(days = 1000)
    date_range = pd.date_range(start_date, current_time, freq = 'C')
    df = pd.DataFrame()

    for date in date_range:
        date_str = date.strftime('%Y%m%d')
        time_str = '15:00'
        datetime_str = date_str + ' ' + time_str
        #get_price is a function which only runs on the company's labtop, it will return the minute trade_volume of 'stock_symbol'
        #stock_symbol contains all the stocks in China's stock market
        value = get_price(stock_symbol, None, datetime_str, '1m', ['volume'], True, None, 240, is_panel = 1) 
        df = df.append(value['volume'])
    return df

trade_volume = concatenate_data(current_date)

trade_volume['date'] = trade_volume.index
trade_volume.to_csv('trade_volume.csv', index = False)
trade_volume = pd.read_csv('trade_volume.csv', index_col = 'date')

#remove the capital number in stock code
trade_volume.index = pd.to_datetime(trade_volume.index)
trade_volume.index = trade_volume.index.normalize()
trade_volume.columns = [str(col).split('.')[0] for col in trade_volume.columns]

def concatenate_quantile(current_time, dataframe):
    df_quantile = pd.DataFrame()
    for date in dataframe.index.unique():
        quantile_90 = dataframe.loc[date].quantile(0.9)
        data = pd.DataFrame([quantile_90.values], columns = quantile_90.index, index = [date])
        df_quantile = df_quantile.append(data, ignore_index = False)
        return df_quantile
    
threshold = concatenate_quantile(current_date, trade_volume)
threshold['date'] = threshold.index
threshold.to_csv('threshold.csv', index = False)
threshold = pd.read_csv('threshold.csv', index_col = 'date')
threshold.index = pd.to_datetime(threshold.index)
threshold.index = threshold.index.normalize()
threshold.columns = [str(col).split('.')[0] for col in threshold.columns]

common_dates = trade_volume.index.intersection(threshold.index).unique()
df = pd.DataFrame()
for idx in common_dates:
    x = trade_volume.loc[idx,:]
    x.index = range(len(x))
    mean_x = x.mean()
    mean_x[mean_x == 0] = np.nan #set 0 to nan to avoid division by 0
    averages = x.apply(lambda x: (x[x > threshold.loc[idx,x.name]].mean())/mean_x[x.name])
    averages = pd.DataFrame(averages).T
    averages.index = [idx]
    df = df.append(averages)

print(df)

df = df.rolling(20).mean() # df = relative_price_factor



#net_support_factor
current_date = datetime.strptime('20240714', '%Y%m%d')

def concatenate_data(current_time):
    start_date = current_time - timedelta(days = 1000)
    date_range = pd.date_range(start_date, current_time, freq = 'C')
    df = pd.DataFrame()

    for date in date_range:
        date_str = date.strftime('%Y%m%d')
        time_str = '15:00'
        datetime_str = date_str + ' ' + time_str
        #get_price is a function which only runs on the company's labtop, it will return the minute trade_volume of 'stock_symbol'
        #stock_symbol contains all the stocks in China's stock market
        value = get_price(stock_symbol, None, datetime_str, '1m', ['close'], True, None, 240, is_panel = 1) 
        df = df.append(value['close'])
    return df
close_price = concatenate_data(current_date)
close_price

def concatenate_average(current_time, dataframe):
    df_mean = pd.DataFrame()
    for date in dataframe.index.unique():
        close_average = dataframe.loc[date].mean()
        data = pd.DataFrame([close_average.values], columns = close_average.index, index = [date])
        df_mean = df_mean.append(data, ignore_index = False)
        return df_mean
df_mean = concatenate_average(current_date, close_price)

df_mean.index = pd.to_datetime(df_mean.index)
df_mean.index = df_mean.index.normalize()
df_mean.columns = [str(col).split('.')[0] for col in df_mean.columns]

common_dates = close_price.index.intersection(df_mean.index).unique()
support_volume = pd.DataFrame()
for idx in common_dates:
    x = close_price.loc[idx,:]
    x.index = range(len(x))
    sums = x.apply(lambda x: (x[x < df_mean.loc[idx,x.name]].sum()))
    sums = pd.DataFrame(sums).T
    sums.index = [idx]
    support_volume = support_volume.append(sums)

resistence_volume = pd.DataFrame()
for idx in common_dates:
    x = close_price.loc[idx,:]
    x.index = range(len(x))
    sums = x.apply(lambda x: (x[x > df_mean.loc[idx,x.name]].sum()))
    sums = pd.DataFrame(sums).T
    sums.index = [idx]
    resistence_volume = resistence_volume.append(sums)

net_support_factor = support_volume - resistence_volume

ashare_float_shares = pd.read_scv('ashare_float_shares.csv', index_col = 'date')

net_support_rolling = net_support_factor.rolling(10).mean()

common_index = net_support_factor.index.interaction(ashare_float_shares.index)
common_columns = net_support_factor.columns.intersection(ashare_float_shares.columns)
net_support_factor_aligned = net_support_factor.loc[common_index, common_columns]
ashare_float_shares_aligned = ashare_float_shares.loc[common_index, common_columns]
net_support_factor_aligned

net_support_division = net_support_factor_aligned / ashare_float_shares_aligned

net_support_division_rolling = net_support_division.rolling(10).mean()