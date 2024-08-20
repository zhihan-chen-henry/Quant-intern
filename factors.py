import pandas as pd
import numpy as np
import scipy.stats
value = pd.DataFrame()

roe = value['close'].pct_change()

vol = roe.rolling(window = 21).std()

skewness = roe.rolling(window = 21).apply(lambda x:scipy.stats.skew(x))

maxret = roe.rolling(window = 21).apply(lambda x:np.mean(sorted(x)[-3:]))

lnto = value['turnover_rate'].rolling(window = 21).mean().apply(np.log)

ret = roe.rolling(window = 21).apply(lambda x: (x+1).prod() - 1)

CGO_3M = value['close'].pct_change(periods = 63)

to = value['turnover_rate'].rolling(window = 21).mean()

illiq = roe.abs()/value['volume']

avg_vol_1m = value['volume'].rolling(window = 21).mean()
avg_vol_12m = value['volume'].rolling(window = 252).mean()
amountvol_1m_12m = avg_vol_1m / avg_vol_12m

#EP = df_net_profit / df_total_mv