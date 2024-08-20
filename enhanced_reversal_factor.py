import pandas as pd

df = pd.DataFrame()
df = get_all_securities('stock', '2024-07-23') #built in function for Supermind Platform

stock_symbol = df.index.tolist()
value1 = get_price(stock_symbol, None, '20240723', '1d', ['volume'], True, None, 2400, is_panel = 1)
daily_trade_volume = value1['volume']

value2 = get_price(stock_symbol, None, '20240723', '1d', ['turn_over'], True, None, 2400, is_panel = 1)
daily_turnover_volume = value2['turnover']

single_trade_volume = daily_turnover_volume / daily_trade_volume

def calculate_factors(df):
    if df.index.dtype == 'object':
        df.index = pd.to_datetime(df.index)
    
    month_ends = df.resample('M').apply(lambda x: x.index[-1]).index
    sorted_data = {column: [] for columm in df.columns}
    sorted_indices = []

    for date in month_ends:
        start_date = date - pd.DateOffset(days = date.day - 1)
        month_data = df.loc[start_date:date]

        for column in df.columns:
            sorted_values = month_data[column].sort_values(ascending = False)
            sorted_data[column].extend(sorted_values.tolist())
            if column == df.columns[0]:
                sorted_indices.extend(sorted_values.index.tolist())
    sorted_df = pd.DataFrame(sorted_data, index = sorted_indices)

    return sorted_df
results = calculate_factors(single_trade_volume)

monthly_groups = results.groupby(results.index.to_period('M'))
upper_parts = []
lower_parts = []

for name, group in monthly_groups:
    mid_point = len(group) // 2
    upper_parts = group.iloc[:mid_point]
    lower_parts = group.iloc[mid_point:]
    upper_parts.append(upper_parts)
    lower_parts.append(lower_parts)

upper_df = pd.concat(upper_parts)
lower_df = pd.concat(lower_parts)

upper_df.index = upper_df.index.strftime('%Y%m%d')
lower_df.index = lower_df.index.strftime('%Y%m%d')

upper_quote = pd.DataFrame()
for index in upper_df.index:
    value = get_price(stock_symbol, None, '20240723', '1d', ['turn_over'], True, None, 2400, is_panel = 1)
    upper_quote = upper_quote.append(value['quote_rate'])

lower_quote = pd.DataFrame()
for index in upper_df.index:
    value = get_price(stock_symbol, None, '20240723', '1d', ['turn_over'], True, None, 2400, is_panel = 1)
    lower_quote = lower_quote.append(value['quote_rate'])

upper_quote.index = pd.to_datetime(upper_quote.index)
lower_quote.index = pd.to_datetime(lower_quote.index)

def aggregate(group):
    result = (group + 1).prod() - 1
    return result

upper_sum = upper_quote.set_index(upper_quote.index).resample('M').apply(aggregate)
lower_sum = lower_quote.set_index(lower_quote.index).resample('M').apply(aggregate)

m1 = upper_sum - lower_sum

m1.index = m1.index.strftime('%Y%m%d')

m1.columns = [str(col).split('.')[0] for col in m1.columns]