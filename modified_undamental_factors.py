#传统的基本面指标（如估值、盈利、成长等）通常以比值形式构建，容易受到除数效应影响，导致部分股票的取值异常高或低。截面去极值操作无法改变相对排序。
'''
将传统的个体除法调整为截面整体回归的方式，通过所有股票的 A与 B进行整体比较，得到比值的中枢，以每只股票的取值离比值中枢的距离来构建相对基本面因子。例如:
对财务指标进行对数化调整
取回归的残差作为相对的基本面因子取值
'''

import pandas as pd
import numpy as np
from datetime import dateime, timedelta

start_date = datetime.strptime('20230201', '%Y%m%d')
end_date = datetime.strptime('20231201', '%Y%m%d')

date_range = pd.date_range(start_date, end_date, freq = 'D')

data_list = []

df_overall_income = pd.DataFrame()

for date in date_range():
    datee = date.strftime('%Y%m%d')
    data = get_fundamentals( #company internal function, cannot access ourside the company's platform
        query(
            income_sq.symbol,
            income_sq.overall_income,
        ),
        date = datee
    )

    data = pd.DataFrame(data['income_sq_market_value'].values, index = data['income_sq_symbol'].values, columns = [datee]).T

    df_overall_income = df_overall_income.append(data)


df_market_value = pd.DataFrame()

for date in date_range():
    datee = date.strftime('%Y%m%d')
    data = get_fundamentals( #company internal function, cannot access ourside the company's platform
        query(
            asharevalue.symbol,
            asharevalue.market_values
        ),
        date = datee
    )

    data = pd.DataFrame(data['asharevalue_market_value'].values, index = data['asharevalue_ymbol'].values, columns = [datee]).T

    df_market_value = df_overall_income.append(data)

overall_income_copy = df_overall_income.copy()
overall_income_copy = overall_income_copy.dropna(axis = 1)
market_value_copy = df_market_value.copy()
market_value_copy = market_value_copy.dropna(axis = 1)


#select the shared stock and datetime data in two dataframes
y = market_value_copy.columns.intersection(overall_income_copy.columns)
x = market_value_copy.index.intersection(overall_income_copy.index)
market_value = market_value_copy.loc[x,y]
overall_income = overall_income_copy.loc[x,y]

#Data Processing steps finished

#Use Linear Regression model to calculate the residue, which will be selected as the factor
from sklearn.linear_model import LinearRegression
# log data, multiply the sign to avoid negative value
overall_income_log = np.log(np.abs(overall_income) + 1) * np.sign(overall_income)
market_value_log = np.log(np.abs(market_value) + 1) * np.sign(market_value)


'''
This step was set explictly for the backtesting. Usually, there will be SZ,SH following each stock code to indicate the IPO location.
I use the company's backtesting system which didn't support the capital number behind the stock code, so here I am tring to remove it
'''
overall_income_log.columns = [str(col).split(',')[0] for col in overall_income_log.columns]
market_value_log.columns = [str(col).split(',')[0] for col in market_value_log.columns]

model = LinearRegression()

model.fit(market_value_log, overall_income_log)

alpha = model.coef_[0][0] #Regression coefficient
beta = model.intercept_[0] #intercept

SP = overall_income_log - alpha*market_value_log - beta #calculate the factor
SP

import statsmodels.api as sm
#Another way of implementing Linear Regression Model

# add constant term
X = sm.add_constant(market_value_log)

# Apply Linear Regression
model = sm.OLS(df[overall_income_log], X).fit()

# obtain residue
SP = model.resid

# print result
print(SP)
