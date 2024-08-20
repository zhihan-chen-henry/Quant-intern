import pandas as pd
import numpy as np

#combined_etf_data = open price of all etf funds
combined_etf_data = pd.DataFrame()

#Calculate the return rate of each RTF everyday
redf = combined_etf_data.shitf(-1)/combined_etf_data - 1

#Another way to calculate return
combined_etf_data['return'] = combined_etf_data.groupby('code')['open'].pct_change().shift(-1)

#Process return data
redf2 = combined_etf_data.pivot(index = 'tradedate', columns = 'code', values = 'return').fillna(0)

#Function to calculate the reversal factor
def calcualte_factors(df, returns_df, N, interval):
    df['tradedate'] = pd.to_datetime(df['tradedate'])
    df = df.sort_values(by = ['code', 'tradedate'])
    results = []

    start_dates = df['tradedate'].iloc[::interval].unique() #select unique trading dates from a DataFrame at regular intervals

    for start_date in start_dates:
        end_date = start_date + pd.Timedelta(days = interval)
        period_df = df[(df['tradedate'] >= start_date) & (df['tradedate'] < end_date)]

        for code, group in period_df.groupby('code'):
            group = group.tail(N)
            
            '''
            Here I tried two ways to calculate the reversal factor M, by using average price or using the return data. After testing, 
            I found using return data will generate more stable profits
            '''
            ##group = group.assign(D = group['avg_price'])
            returns = returns_df.loc[group['tradedate'],code].values
            group['return'] = returns
            group = group.assign(D = group['return'])
            ###group['D'] = returns_df.loc[group['tradedate'],code].values  #Same meaning as three lines of codes above

            group = group.sort_values(by = 'D', ascending = False)

            high_D = group.head(N//2)
            low_D = group.tail(N//2)

            M_high = high_D['return'].add(1).cumprod().iloc[-1] - 1 #Factor value of high D group
            M_low = low_D['return'].add(1).cumprod().iloc[-1] - 1 #Factor value of low D group

            M = M_high - M_low

            results.append({
                'tradedate': start_date,
                'code': code,
                'M_high': M_high,
                'M_low': M_low,
                'M': M
            })


N = 20
interval = 20
results = calcualte_factors(combined_etf_data, redf2, N, interval)

sorted_results = results.sort_values(by = ['tradedate', 'M'], ascending = [True, False]) # Select the etf with largest Ms

unique_dates = sorted_results['tradedate'].unique()
result_df = pd.DataFrame()


'''
This part was my trading strategy, based on the above code, I have selcted out the etf with largest M factor values everyday,
now I will buy etfs with top 3 largest M at the next day. For example, on Jan 1st, etf A,B,C has largest M factor value, then I will buy A,B,C at Jan 2nd.
'''
#Iterates through every tradetime
for i, date in enumerate(unique_dates):
    current_df = sorted_results[sorted_results['tradedate'] == date].copy()
    
    # if not the last tradedate, switch this tradedate to next one
    if i < len(unique_dates) - 1:
        current_df['tradedate'] = unique_dates[i + 1]
    else:
        current_df['tradedate'] = pd.NaT
    
    result_df = pd.concat([result_df, current_df], ignore_index=True)

# last tradedate is Nan
result_df.loc[result_df['tradedate'].isna(), ['code']] = None
result_df.set_index('tradedate', inplace=True)

'''
Process the dataFrame, drop some values that I no longer use
'''
result_df = result_df.drop(columns = ['M_high'])
result_df = result_df.drop(columns = ['M_low'])
result_df = result_df.drop(columns = ['M'])
result_df = result_df.reset_index(inplace = True)
result_df = result_df.dropna(subset = ['tradedate'])

'''
Take the tranpose of the result_df
'''
new = pd.DataFrame()
for date, group in result_df.groupby('tradedate'):
    codes = group['code'].values[:25] #25 etfs in total
    if len(codes) < 25:
        codes = list(codes) + [None] * (25 - len(codes))
    new = new.append(pd.Series(codes, name=date))

#set the col index from 0 to 24
new.columns = range(25)
new.index.name = 'tradedate'

'''
replace ETF data with the return data
'''
redf.index = [pd.to_datetime(i) for i in redf.index]
df = new.apply(lambda x: pd.Series([redf.loc[x.name, i] if i else np.nan for i in x]), axis = 1)

'''
Now I got a df with col index 0-24, row index tradedate, values are the return rate of all etfs, 
I will select the top 3 etf with highest total return, then second top 3, then third ...
there will be 9 groups, with last group only have one etf with lowest total return
the return will be a df with col index 0-8, row index unchanged, but value is the mean of three etfs at that day.
'''
group_indices = [list(range(i,i+3)) for i in range(0,22,3)] + [list(range(24,25))]
new_columns = range(len(group_indices))
new_df = pd.DataFrame(index = df.index, columns = new_columns)

for i, indices in enumerate(group_indices):
    new_df[i] = df.iloc[:, indices].mean(axis = 1)

'''
Finally, plot the cumulative return
'''
new_df.index = [str(i) for i in new_df.index]
(new_df+1).cumprod().plot()
